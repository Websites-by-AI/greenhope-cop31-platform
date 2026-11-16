"""KAG (Knowledge-Augmented Generation) engine for per-investor logical reasoning and structured form filling.

Uses a typed NetworkX directed Knowledge Graph (KG) dedicated strictly to ONE investor.
Performs multi-hop graph traversal for:
  - Applicant type & geography mandate matching
  - Sector alignment & financial instrument/ticket constraint solving
  - Exclusion list screening & mandatory compliance rule verification
  - Graph-path grounded form-field population with explicit logical traces
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from ..forms.form_templates import get_form_template
from ..security.tenant_guard import PIIRedactor, TenantIsolationGuard
from .llm_adapter import GroundedLLMAdapter
from .schemas import (
    ApplicantProject,
    EligibilityEvaluation,
    FieldFillStatus,
    FilledFormField,
    FormFieldSpec,
    InvestorRecord,
)

# Normalized geography hierarchy so multi-hop KG matching handles regional membership accurately
COUNTRY_REGION_MAP: Dict[str, List[str]] = {
    "türkiye": ["türkiye", "turkey", "emea", "europe", "emerging markets", "developing countries", "oic", "global"],
    "turkey": ["türkiye", "turkey", "emea", "europe", "emerging markets", "developing countries", "oic", "global"],
    "egypt": ["egypt", "africa", "mena", "emea", "emerging markets", "developing countries", "oic", "global"],
    "morocco": ["morocco", "africa", "mena", "emea", "emerging markets", "developing countries", "oic", "global"],
    "kenya": ["kenya", "africa", "sub-saharan africa", "emerging markets", "developing countries", "global"],
    "south africa": ["south africa", "africa", "sub-saharan africa", "emerging markets", "developing countries", "global"],
    "brazil": ["brazil", "latin america", "lac", "americas", "emerging markets", "developing countries", "global"],
    "india": ["india", "asia", "south asia", "asia-pacific", "emerging markets", "developing countries", "global"],
    "indonesia": ["indonesia", "asia", "asia-pacific", "emerging markets", "developing countries", "oic", "global"],
    "kazakhstan": ["kazakhstan", "central asia", "asia", "emea", "emerging markets", "developing countries", "oic", "global"],
    "germany": ["germany", "europe", "eu", "emea", "global"],
    "spain": ["spain", "europe", "eu", "emea", "global"],
    "united kingdom": ["united kingdom", "uk", "europe", "emea", "global"],
    "nepal": ["nepal", "asia", "south asia", "asia-pacific", "ldc", "emerging markets", "developing countries", "global"],
}


def _slug(text: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in text.lower()).strip("_")


class InvestorKAGEngine:
    """Dedicated Knowledge-Augmented Generation engine scoped strictly to one COP31 investor."""

    def __init__(
        self,
        investor: InvestorRecord,
        graph: nx.DiGraph,
        tenant_guard: Optional[TenantIsolationGuard] = None,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> None:
        if tenant_guard is not None:
            tenant_guard.assert_investor_match(investor.investor_id)
        self.investor = investor
        self.graph = graph
        self.tenant_guard = tenant_guard
        self.llm = llm_adapter or GroundedLLMAdapter()

    @classmethod
    def build_for_investor(
        cls,
        investor: InvestorRecord,
        tenant_guard: Optional[TenantIsolationGuard] = None,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> "InvestorKAGEngine":
        """Construct a rich typed Knowledge Graph strictly from this investor's verified profile and form schema."""
        if tenant_guard is not None:
            tenant_guard.assert_investor_match(investor.investor_id)

        g = nx.DiGraph()
        root_id = investor.investor_id
        g.add_node(
            root_id,
            node_type="Investor",
            investor_id=investor.investor_id,
            name=investor.name,
            short_name=investor.short_name,
            category=investor.category.value,
            hq_country=investor.hq_country,
            ticket_min_usd=investor.typical_ticket_min_usd,
            ticket_max_usd=investor.typical_ticket_max_usd,
            portal_url=investor.application_portal_url,
        )

        # COP31 Commitment Node
        cop_node = f"cop31::{root_id}"
        g.add_node(
            cop_node,
            node_type="COP31_Commitment",
            investor_id=root_id,
            role=investor.cop31_antalya_role,
            commitment=investor.cop31_verified_2026_commitment,
            verification_source=investor.verification_source_url,
            verification_date=investor.verification_date,
        )
        g.add_edge(root_id, cop_node, relation="ANNOUNCES_AT_COP31")

        # Instruments
        for inst in investor.financing_instruments:
            node_id = f"instrument::{_slug(inst)}"
            g.add_node(node_id, node_type="Instrument", investor_id=root_id, label=inst)
            g.add_edge(root_id, node_id, relation="OFFERS_INSTRUMENT")

        # Target Sectors
        for sec in investor.target_sectors:
            node_id = f"sector::{_slug(sec)}"
            g.add_node(node_id, node_type="TargetSector", investor_id=root_id, label=sec)
            g.add_edge(root_id, node_id, relation="FUNDS_SECTOR")

        # Geographies
        for geo in investor.geographic_focus:
            node_id = f"region::{_slug(geo)}"
            g.add_node(node_id, node_type="Geography", investor_id=root_id, label=geo)
            g.add_edge(root_id, node_id, relation="COVERS_REGION")

        # Eligible Applicant Types
        for app_type in investor.eligible_applicant_types:
            node_id = f"applicant::{_slug(app_type)}"
            g.add_node(node_id, node_type="EligibleApplicant", investor_id=root_id, label=app_type)
            g.add_edge(root_id, node_id, relation="ACCEPTS_APPLICANT")

        # Mandatory Compliance Requirements
        req_nodes: List[Tuple[str, str]] = []
        for req in investor.mandatory_form_requirements:
            node_id = f"rule::{_slug(req)[:48]}"
            g.add_node(node_id, node_type="MandatoryRequirement", investor_id=root_id, label=req)
            g.add_edge(root_id, node_id, relation="REQUIRES_COMPLIANCE")
            req_nodes.append((node_id, req.lower()))

        # Exclusion Rules
        for excl in investor.exclusion_rules:
            node_id = f"exclusion::{_slug(excl)[:48]}"
            g.add_node(node_id, node_type="ExclusionRule", investor_id=root_id, label=excl)
            g.add_edge(root_id, node_id, relation="EXCLUDES")

        # Form Template & Field Nodes + Rule-to-Field Validation Links
        template = get_form_template(investor.form_template_type)
        tpl_node = f"form::{template.template_id.value}"
        g.add_node(
            tpl_node,
            node_type="FormTemplate",
            investor_id=root_id,
            title=template.title,
            governing_standard=template.governing_standard,
        )
        g.add_edge(root_id, tpl_node, relation="USES_FORM_TEMPLATE")

        for field in template.fields:
            f_node = f"field::{field.field_id}"
            g.add_node(
                f_node,
                node_type="FormField",
                investor_id=root_id,
                field_id=field.field_id,
                label=field.label,
                section=field.section,
                strategy=field.generation_strategy,
                required=field.required,
            )
            g.add_edge(tpl_node, f_node, relation="HAS_FORM_FIELD")

            # Link matching compliance rules directly to the form field they govern (word-boundary matched)
            f_text = f"{field.field_id} {field.label} {field.description}".lower()
            for r_node, r_lower in req_nodes:
                if any(
                    re.search(rf"\b{re.escape(kw)}\b", f_text) and re.search(rf"\b{re.escape(kw)}\b", r_lower)
                    for kw in ["paris", "nda", "eia", "safeguards", "cbam", "kgf", "shariah", "spo", "accredited", "taxonomy", "ghg", "ifc"]
                ):
                    g.add_edge(r_node, f_node, relation="VALIDATES_FIELD")

        return cls(investor=investor, graph=g, tenant_guard=tenant_guard, llm_adapter=llm_adapter)

    def save(self, path: Path) -> None:
        if self.tenant_guard is not None:
            self.tenant_guard.assert_path_within_tenant(path)
        payload = {
            "investor_id": self.investor.investor_id,
            "graph_format": "networkx-node-link-v1",
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "graph": nx.node_link_data(self.graph, edges="links"),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(
        cls,
        investor: InvestorRecord,
        path: Path,
        tenant_guard: Optional[TenantIsolationGuard] = None,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> "InvestorKAGEngine":
        if tenant_guard is not None:
            tenant_guard.assert_path_within_tenant(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if tenant_guard is not None:
            tenant_guard.assert_investor_match(payload["investor_id"])
        g = nx.node_link_graph(payload["graph"], edges="links")
        # Verify zero cross-tenant nodes leaked into the graph
        for _, attrs in g.nodes(data=True):
            if attrs.get("investor_id") != investor.investor_id:
                raise PermissionError(f"Cross-tenant KG node detected inside {investor.investor_id}'s graph!")
        return cls(investor=investor, graph=g, tenant_guard=tenant_guard, llm_adapter=llm_adapter)

    def _neighbors_by_relation(self, relation: str) -> List[Tuple[str, Dict[str, Any]]]:
        root = self.investor.investor_id
        results: List[Tuple[str, Dict[str, Any]]] = []
        for _, target, edge_data in self.graph.out_edges(root, data=True):
            if edge_data.get("relation") == relation:
                results.append((target, dict(self.graph.nodes[target])))
        return results

    def evaluate_eligibility(self, project: ApplicantProject) -> EligibilityEvaluation:
        """Run deterministic multi-hop KG reasoning across applicant type, region, sector, ticket, exclusions & rules."""
        passed: List[str] = []
        failed: List[str] = []
        warnings: List[str] = []
        score = 0.0
        hops = 0

        # Hop 1: Applicant Type
        hops += 1
        accepted_types = [attrs["label"] for _, attrs in self._neighbors_by_relation("ACCEPTS_APPLICANT")]
        app_lower = project.applicant_type.lower()
        applicant_match = any(
            app_lower in a.lower() or a.lower() in app_lower
            for a in accepted_types
        )
        if applicant_match:
            passed.append(f"Applicant type '{project.applicant_type}' matched via ACCEPTS_APPLICANT ({', '.join(accepted_types)}).")
            score += 22.0
        else:
            # Check if intermediary channel is available (e.g., Climate Funds via Accredited Entity)
            if any("intermediary" in a.lower() or "accredited" in a.lower() for a in accepted_types):
                warnings.append(
                    f"Direct applicant '{project.applicant_type}' requires channeling through an Accredited Entity / Financial Intermediary."
                )
                score += 10.0
            else:
                failed.append(f"Applicant type '{project.applicant_type}' not directly in accepted list: {accepted_types}.")

        # Hop 2: Geography Mandate
        hops += 1
        covered_geos = [attrs["label"] for _, attrs in self._neighbors_by_relation("COVERS_REGION")]
        country_tokens = set(COUNTRY_REGION_MAP.get(project.country.lower(), [project.country.lower(), project.region.lower(), "global"]))
        country_tokens.add(project.region.lower())
        geo_match = any(
            any(tok in g.lower() or g.lower() in tok for tok in country_tokens)
            for g in covered_geos
        )
        if geo_match:
            passed.append(f"Geography '{project.country} ({project.region})' covered via COVERS_REGION ({', '.join(covered_geos)}).")
            score += 20.0
        else:
            failed.append(f"Host country '{project.country}' outside investor geographic mandate: {covered_geos}.")

        # Hop 3: Sector Overlap
        hops += 1
        funded_sectors = [attrs["label"] for _, attrs in self._neighbors_by_relation("FUNDS_SECTOR")]
        proj_sectors = [project.primary_sector] + list(project.secondary_sectors)
        matched_sectors: List[str] = []
        for ps in proj_sectors:
            ps_words = {w for w in ps.lower().replace("/", " ").replace("-", " ").split() if len(w) > 3}
            for fs in funded_sectors:
                fs_words = {w for w in fs.lower().replace("/", " ").replace("-", " ").split() if len(w) > 3}
                if ps.lower() in fs.lower() or fs.lower() in ps.lower() or (ps_words & fs_words):
                    matched_sectors.append(fs)
        matched_sectors = sorted(set(matched_sectors))
        if matched_sectors:
            passed.append(f"Sector alignment verified via FUNDS_SECTOR: {', '.join(matched_sectors[:4])}.")
            score += 23.0
        else:
            failed.append(f"Project sector '{project.primary_sector}' does not align with investor sectors: {funded_sectors}.")

        # Hop 4: Ticket Size & Instrument Constraint Solving
        hops += 1
        root_attrs = self.graph.nodes[self.investor.investor_id]
        t_min = root_attrs["ticket_min_usd"]
        t_max = root_attrs["ticket_max_usd"]
        if t_min <= project.requested_amount_usd <= t_max:
            passed.append(f"Requested ticket ${project.requested_amount_usd:,.0f} fits within bounds (${t_min:,.0f}–${t_max:,.0f}).")
            score += 15.0
        elif project.requested_amount_usd < t_min:
            warnings.append(
                f"Requested ticket ${project.requested_amount_usd:,.0f} is below typical minimum (${t_min:,.0f}); consider aggregation or on-lending credit line."
            )
            score += 6.0
        else:
            warnings.append(
                f"Requested ticket ${project.requested_amount_usd:,.0f} exceeds single-ticket ceiling (${t_max:,.0f}); syndicated/co-financing structure required."
            )
            score += 6.0

        offered_instruments = [attrs["label"] for _, attrs in self._neighbors_by_relation("OFFERS_INSTRUMENT")]
        chosen_instrument = offered_instruments[0] if offered_instruments else "Climate Finance Facility"
        inst_matched = False
        for pref in project.preferred_instruments:
            for off in offered_instruments:
                if pref.lower() in off.lower() or off.lower() in pref.lower():
                    chosen_instrument = off
                    inst_matched = True
                    break
            if inst_matched:
                break
        if inst_matched:
            passed.append(f"Instrument match via OFFERS_INSTRUMENT: '{chosen_instrument}'.")
            score += 10.0
        else:
            warnings.append(
                f"Preferred instruments {project.preferred_instruments} differ from primary menu {offered_instruments}; defaulted to '{chosen_instrument}'."
            )
            score += 4.0

        # Hop 5: Exclusion List Check
        hops += 1
        exclusions = [attrs["label"] for _, attrs in self._neighbors_by_relation("EXCLUDES")]
        if project.fossil_fuel_involvement and any("fossil" in e.lower() or "coal" in e.lower() for e in exclusions):
            failed.append("HARD EXCLUSION BREACH: Project involves fossil fuels, violating investor EXCLUDES rule.")
            score = max(0.0, score - 40.0)
        else:
            passed.append("Exclusion list screening passed (no prohibited coal/unabated fossil-fuel activities).")
            score += 5.0

        # Hop 6: Mandatory Compliance Rules Check
        hops += 1
        rules = [attrs["label"] for _, attrs in self._neighbors_by_relation("REQUIRES_COMPLIANCE")]
        rule_blob = " | ".join(rules).lower()
        compliance_penalties = 0
        if "nda" in rule_blob and not project.has_nda_no_objection_letter:
            warnings.append("Missing mandatory NDA / Operational Focal Point No-Objection Letter (required before final submission).")
            compliance_penalties += 1
        if "shariah" in rule_blob and not project.shariah_compliant_structure:
            warnings.append("Investor requires Shariah-compliant financing structure (Murabaha/Istisna'a/Sukuk); structure confirmation needed.")
            compliance_penalties += 1
        if ("paris" in rule_blob or "ndc" in rule_blob) and not project.has_paris_alignment_assessment:
            warnings.append("Paris Agreement Alignment (BB1/BB2) assessment not yet finalized; KAG drafted preliminary screening.")
        if ("eia" in rule_blob or "environmental" in rule_blob) and not project.has_eia_and_permits:
            warnings.append("Environmental Impact Assessment (EIA / ÇED) permits pending; must attach before appraisal.")
        if compliance_penalties == 0:
            passed.append("No hard pre-submission compliance blockers detected in REQUIRES_COMPLIANCE graph.")
            score += 5.0
        else:
            score += 2.0

        eligible = (len(failed) == 0) and (score >= 55.0)
        return EligibilityEvaluation(
            eligible=eligible,
            fit_score=round(min(100.0, score), 1),
            passed_checks=passed,
            failed_checks=failed,
            warnings=warnings,
            recommended_instrument=chosen_instrument,
            kag_hops_executed=hops,
        )

    def fill_field(
        self,
        field: FormFieldSpec,
        project: ApplicantProject,
        eligibility: EligibilityEvaluation,
        rag_snippets: Optional[List[Dict[str, Any]]] = None,
    ) -> FilledFormField:
        """Populate a single form field using Knowledge Graph paths + applicant data (with optional RAG enrichment)."""
        root = self.investor.investor_id
        cop_attrs = self.graph.nodes[f"cop31::{root}"]
        rules = [attrs["label"] for _, attrs in self._neighbors_by_relation("REQUIRES_COMPLIANCE")]
        instruments = [attrs["label"] for _, attrs in self._neighbors_by_relation("OFFERS_INSTRUMENT")]
        sectors = [attrs["label"] for _, attrs in self._neighbors_by_relation("FUNDS_SECTOR")]
        geos = [attrs["label"] for _, attrs in self._neighbors_by_relation("COVERS_REGION")]

        # Determine validating rules connected to this specific field in the KG
        field_node = f"field::{field.field_id}"
        validating_rules = [
            self.graph.nodes[src]["label"]
            for src, _, edata in self.graph.in_edges(field_node, data=True)
            if edata.get("relation") == "VALIDATES_FIELD"
        ]

        fid = field.field_id
        status = FieldFillStatus.FILLED
        confidence = 0.90
        notes: List[str] = []
        kg_path = f"{root} --[USES_FORM_TEMPLATE]--> form::{self.investor.form_template_type.value} --[HAS_FORM_FIELD]--> {field_node}"
        value: Any = ""

        # 1. Applicant direct fields (PII-safe)
        if fid in {"project_title", "sponsor_and_project", "borrower_profile", "company_and_project"}:
            value = f"{project.project_title} | Sponsor: {project.organization_name} ({project.applicant_type}) | Jurisdiction: {project.country} ({project.region}) | Primary Sector: {project.primary_sector}"
            confidence = 0.98
        elif fid == "company_identity_masked":
            masked_tax = PIIRedactor.mask_identifier(project.tax_or_registration_id)
            value = f"{project.organization_name} | Tax/VKN (Masked): {masked_tax} | Country: {project.country}"
            if not project.tax_or_registration_id:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Tax/VKN ID missing; inject securely via encrypted export before bank submission.")
                confidence = 0.72
            else:
                notes.append("Tax/VKN masked inside AI context via PIIRedactor; re-hydrate only on final portal export.")
                confidence = 0.95
        elif fid in {"financial_viability_metrics", "financial_profile", "financial_snapshot", "credit_financials"}:
            parts = [f"Total Project Capex: ${project.total_project_cost_usd:,.0f}"]
            if project.annual_revenue_usd is not None:
                parts.append(f"Annual Revenue: ${project.annual_revenue_usd:,.0f}")
            if project.ebitda_usd is not None:
                parts.append(f"EBITDA: ${project.ebitda_usd:,.0f}")
            if project.expected_irr_percent is not None:
                parts.append(f"Projected IRR: {project.expected_irr_percent:.1f}%")
            value = " | ".join(parts)
            if project.annual_revenue_usd is None or project.ebitda_usd is None:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Audited revenue/EBITDA statements should be attached prior to credit committee review.")
                confidence = 0.76
            else:
                confidence = 0.94
        elif fid == "implementation_timeline":
            value = f"Current Maturity: {project.project_stage} | Expected Implementation Horizon: {project.implementation_years} years"
            confidence = 0.96

        # 2. KAG Logical Rule Fields
        elif fid == "sovereign_window":
            is_pub = any(k in project.applicant_type.lower() for k in ["sovereign", "government", "municipality"])
            window = "Sovereign / Sub-Sovereign Public Window" if is_pub else "Non-Sovereign Operations (NSO) / Private Sector Window"
            value = f"{window} (Derived from applicant_type='{project.applicant_type}' against {self.investor.short_name} mandate)"
            kg_path = f"{root} --[ACCEPTS_APPLICANT]--> applicant::{_slug(project.applicant_type)} => {window}"
            confidence = 0.95
        elif fid == "enterprise_segment":
            seg = project.applicant_type
            if project.eu_cbam_exporter:
                seg += " / EU CBAM-Exposed Exporter"
            value = seg
            kg_path = f"{root} --[ACCEPTS_APPLICANT]--> {seg}"
            confidence = 0.95
        elif fid in {"requested_instrument_and_amount", "funding_window_and_instrument", "financing_request", "loan_amount_and_maturity", "facility_structure", "round_and_instrument"}:
            t_min = self.investor.typical_ticket_min_usd
            t_max = self.investor.typical_ticket_max_usd
            in_bounds = t_min <= project.requested_amount_usd <= t_max
            value = (
                f"Instrument: {eligibility.recommended_instrument} | Requested Amount: ${project.requested_amount_usd:,.0f} USD "
                f"| Tenor/Horizon: {project.implementation_years} years | Investor Band: ${t_min:,.0f}–${t_max:,.0f} "
                f"({'WITHIN BOUNDS' if in_bounds else 'REQUIRES CO-FINANCING/AGGREGATION'})"
            )
            kg_path = f"{root} --[OFFERS_INSTRUMENT]--> {eligibility.recommended_instrument} [bounds: ${t_min:,.0f}-${t_max:,.0f}]"
            if not in_bounds:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Requested amount falls outside typical single-ticket bounds; consider blended co-financing.")
                confidence = 0.78
            else:
                confidence = 0.94
        elif fid == "accredited_entity_pathway":
            if "accredited" in project.applicant_type.lower() or "sovereign" in project.applicant_type.lower():
                value = f"Direct / Accredited Submission Eligible ({project.organization_name} qualifies under {self.investor.short_name} channel)."
                confidence = 0.92
            else:
                value = (
                    f"INTERMEDIARY CHANNEL REQUIRED: '{project.applicant_type}' must submit to {self.investor.short_name} via an Accredited Entity "
                    f"(e.g., EBRD, World Bank, ADB, AfDB, TSKB, BNDES, or national Direct Access Entity)."
                )
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Partner with a GCF/AF/GEF Accredited Entity before formal portal upload.")
                confidence = 0.84
            kg_path = f"{root} --[REQUIRES_COMPLIANCE]--> Accredited_Entity_Channel --[VALIDATES_FIELD]--> {field_node}"
        elif fid == "nda_no_objection_status":
            if project.has_nda_no_objection_letter:
                value = f"VERIFIED: Host-country ({project.country}) NDA / Operational Focal Point No-Objection Letter confirmed available."
                confidence = 0.96
            else:
                value = f"ACTION REQUIRED: NDA / Operational Focal Point No-Objection Letter from {project.country} is NOT yet attached (mandatory for {self.investor.short_name})."
                status = FieldFillStatus.MISSING_REQUIRED_DATA
                notes.append(f"Obtain official NDA No-Objection Letter from {project.country}'s UNFCCC Focal Point before submission.")
                confidence = 0.88
            kg_path = f"{root} --[REQUIRES_COMPLIANCE]--> NDA_No_Objection --[VALIDATES_FIELD]--> {field_node}"
        elif fid == "paris_alignment_bb1_bb2":
            if project.has_paris_alignment_assessment:
                value = (
                    f"ALIGNED (BB1 Mitigation & BB2 Adaptation Verified): Formal Paris Alignment screening completed for {project.primary_sector}; "
                    f"zero unabated fossil-fuel lock-in; aligned with {project.country} NDC targets."
                )
                confidence = 0.94
            else:
                value = (
                    f"PRELIMINARY ALIGNMENT (Formal BB1/BB2 Sign-Off Pending): Project targets {project.primary_sector} with zero fossil-fuel exposure; "
                    f"complete Joint MDB Paris Alignment BB1/BB2 checklist prior to Concept Clearance."
                )
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Attach formal Joint MDB Paris Alignment BB1/BB2 worksheet.")
                confidence = 0.80
            kg_path = f"{root} --[REQUIRES_COMPLIANCE]--> Paris_Alignment_BB1_BB2 --[VALIDATES_FIELD]--> {field_node}"
        elif fid in {"es_safeguards_category", "ifc_ps_esg_compliance", "environmental_permits_status", "esg_controversy_screen", "esg_impact_governance"}:
            excl_ok = not project.fossil_fuel_involvement
            eia_txt = "EIA / ÇED permits obtained" if project.has_eia_and_permits else "EIA / environmental permitting in progress (condition precedent)"
            shariah_txt = ""
            if any("shariah" in r.lower() for r in rules):
                shariah_txt = f" | Shariah Compliance: {'Confirmed' if project.shariah_compliant_structure else 'Pending Shariah Board review'}"
            value = (
                f"Exclusion Screening: {'PASS (Zero prohibited fossil-fuel exposure)' if excl_ok else 'FAIL (Fossil-fuel exclusion triggered)'} "
                f"| E&S / Permits: {eia_txt}{shariah_txt} | Social/ESG Impact: {project.esg_and_social_impact}"
            )
            if not excl_ok:
                status = FieldFillStatus.MISSING_REQUIRED_DATA
                notes.append("Fossil-fuel involvement breaches investor exclusion policy.")
                confidence = 0.92
            elif not project.has_eia_and_permits:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Attach approved EIA / environmental permits prior to credit/board approval.")
                confidence = 0.81
            else:
                confidence = 0.93
            kg_path = f"{root} --[EXCLUDES + REQUIRES_COMPLIANCE]--> {field_node}"
        elif fid == "geography_and_sector_fit":
            value = (
                f"Mandate Verification: Country={project.country} vs Investor Geographies={', '.join(geos[:4])} | "
                f"Sector={project.primary_sector} vs Investor Sectors={', '.join(sectors[:4])} | "
                f"KAG Fit Score={eligibility.fit_score}/100 ({'ELIGIBLE' if eligibility.eligible else 'CONDITIONAL/REVIEW'})"
            )
            kg_path = f"{root} --[COVERS_REGION + FUNDS_SECTOR]--> MandateFit({eligibility.fit_score})"
            confidence = 0.94 if eligibility.eligible else 0.78
            if not eligibility.eligible:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
        elif fid == "collateral_and_kgf_status":
            if project.has_kgf_or_collateral:
                value = "ELIGIBLE: Applicant holds bankable collateral / Kredi Garanti Fonu (KGF) guarantee eligibility for green credit underwriting."
                confidence = 0.93
            else:
                value = "REVIEW REQUIRED: Collateral or KGF guarantee package not yet confirmed; evaluate KGF Green Transformation guarantee window."
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Confirm collateral assets or apply for KGF Treasury-backed sustainability guarantee.")
                confidence = 0.76
            kg_path = f"{root} --[REQUIRES_COMPLIANCE]--> Collateral_KGF_Rule --[VALIDATES_FIELD]--> {field_node}"
        elif fid == "inclusive_priority_flags":
            flags = []
            if project.women_or_youth_led:
                flags.append("Women/Youth-Led Enterprise Priority (eligible for preferential COP31/ADB/Halkbank/Akbank terms)")
            if project.eu_cbam_exporter:
                flags.append("EU CBAM Exporter Priority")
            value = " | ".join(flags) if flags else "Standard Commercial Green Eligibility (no special inclusive-finance sub-quota flagged)"
            confidence = 0.94
        elif fid == "spo_and_verification":
            if project.has_second_party_opinion:
                value = "READY: External Second-Party Opinion (SPO) & independent GHG verification framework confirmed."
                confidence = 0.95
            else:
                value = "PENDING: External Second-Party Opinion (SPO — e.g., Sustainalytics / ISS / S&P Shades of Green) recommended for Green Loan / SLL / Bond labeling."
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Commission SPO or align KPIs with LMA GLP/SLLP prior to syndication.")
                confidence = 0.80

        # 3. Hybrid / Structured Climate & Narrative Fields
        else:
            cop_role = cop_attrs["role"]
            cop_commit = cop_attrs["commitment"]
            ghg_str = (
                f"{project.estimated_ghg_reduction_tco2e_per_year:,.0f} tCO2e/year avoided"
                if project.estimated_ghg_reduction_tco2e_per_year
                else "GHG mitigation baseline under quantification"
            )
            adap_str = (
                f"{project.adaptation_beneficiaries:,} direct adaptation beneficiaries"
                if project.adaptation_beneficiaries
                else "climate resilience co-benefits embedded"
            )
            cofin_ratio = (
                (project.co_financing_committed_usd / project.requested_amount_usd)
                if project.requested_amount_usd > 0
                else 0.0
            )
            rag_note = ""
            if rag_snippets:
                top_ids = ", ".join(f"[{s['chunk_id']}]" for s in rag_snippets[:2])
                rag_note = f" Grounded in policy references {top_ids}."

            if fid in {"cop31_platform_alignment", "dfi_facility_alignment", "bank_green_program", "climate_thesis_fit"}:
                value = (
                    f"Aligns directly with {self.investor.name}'s COP31 Antalya role ({cop_role}) and 2026 commitment ({cop_commit}). "
                    f"{project.project_title} deploys {project.primary_sector} in {project.country}, fitting priority sectors ({', '.join(sectors[:3])}) "
                    f"via {eligibility.recommended_instrument}.{rag_note}"
                )
                kg_path = f"{root} --[ANNOUNCES_AT_COP31]--> cop31::{root} + --[FUNDS_SECTOR]--> {project.primary_sector}"
            elif fid in {"cofinancing_structure", "cofinancing_leverage", "capital_stack_and_cofinanciers"}:
                sponsor_gap = max(0, project.total_project_cost_usd - project.requested_amount_usd - project.co_financing_committed_usd)
                value = (
                    f"Total Cost: ${project.total_project_cost_usd:,.0f} | Requested from {self.investor.short_name}: ${project.requested_amount_usd:,.0f} "
                    f"({eligibility.recommended_instrument}) | Committed Co-Financing: ${project.co_financing_committed_usd:,.0f} "
                    f"(Leverage Ratio: {cofin_ratio:.2f}x) | Remaining Sponsor Equity / Co-Investor Mobilization: ${sponsor_gap:,.0f}.{rag_note}"
                )
            elif fid in {"ghg_and_adaptation_impact", "mitigation_adaptation_metrics", "avoided_emissions_and_dev_impact", "carbon_and_cbam_impact", "decarbonization_unit_economics"}:
                cbam_note = " Directly mitigates EU CBAM carbon border liability for Turkish/regional exports." if project.eu_cbam_exporter else ""
                irr_note = f" Projected commercial IRR: {project.expected_irr_percent:.1f}%." if project.expected_irr_percent else ""
                value = (
                    f"Quantified Climate Impact: {ghg_str}; {adap_str}. {project.climate_rationale}{cbam_note}{irr_note}{rag_note}"
                )
            elif fid in {"key_risks_and_mitigants", "risks_and_mitigants"}:
                value = f"{project.key_risks_and_mitigants} Supported by {self.investor.short_name} risk-sharing instruments ({', '.join(instruments[:3])}).{rag_note}"
            elif fid in {"technology_and_moat", "eligible_green_use_of_proceeds", "use_of_proceeds_narrative"}:
                value = (
                    f"Use of Proceeds ({project.primary_sector}): {project.technology_and_innovation} "
                    f"Eligibility Requirements Checked: {'; '.join(rules[:2])}.{rag_note}"
                )
            elif fid in {"gender_and_social_inclusion"}:
                incl = "Women/youth leadership confirmed. " if project.women_or_youth_led else ""
                value = f"{incl}{project.esg_and_social_impact}{rag_note}"
            elif fid == "paradigm_shift_potential":
                value = (
                    f"Systemic Scalability & Replicability: {project.project_title} establishes a replicable {project.primary_sector} model "
                    f"across {project.country} ({project.region}) leveraging {project.technology_and_innovation} "
                    f"Designed for scale-up aligned with {self.investor.short_name}'s COP31 Antalya implementation pathway.{rag_note}"
                )
            elif fid == "climate_rationale_additionality":
                value = (
                    f"Climate Rationale & Financial Additionality: {project.climate_rationale} "
                    f"Concessional/catalytic participation from {self.investor.short_name} (${project.requested_amount_usd:,.0f}) de-risks "
                    f"upfront capex (${project.total_project_cost_usd:,.0f}) that domestic commercial markets alone do not bridge at viable tenors ({project.implementation_years} yrs).{rag_note}"
                )
            elif fid == "monitoring_and_exit_strategy":
                value = (
                    f"MRV & Post-Funding Sustainability: Annual verified GHG tracking ({ghg_str}) and beneficiary monitoring ({adap_str}) "
                    f"over the {project.implementation_years}-year deployment horizon. Self-sustaining commercial exit backed by "
                    f"{f'projected {project.expected_irr_percent:.1f}% IRR and operating cash flows' if project.expected_irr_percent else 'institutional operations and local revenue recovery'}.{rag_note}"
                )
            elif fid == "taxonomy_alignment":
                value = (
                    f"Taxonomy Alignment: {project.primary_sector} ({', '.join(project.secondary_sectors) or 'Climate Mitigation/Resilience'}) "
                    f"maps to eligible green activities under EU Taxonomy / ICMA GBP / LMA GLP and {self.investor.short_name} framework ({'; '.join(rules[:2])}).{rag_note}"
                )
            elif fid == "spts_and_kpis":
                value = (
                    f"Proposed KPIs & SPTs: KPI-1 Absolute GHG Abatement ({ghg_str}); KPI-2 Climate Resilience / Co-Benefits ({adap_str}); "
                    f"verified annually over the {project.implementation_years}-year facility tenor aligned with {self.investor.short_name} sustainability reporting.{rag_note}"
                )
            elif fid == "blended_finance_and_ta":
                value = (
                    f"Blended Structure & Technical Assistance: Pairs ${project.requested_amount_usd:,.0f} ({eligibility.recommended_instrument}) with "
                    f"${project.co_financing_committed_usd:,.0f} committed co-financing (leverage {cofin_ratio:.2f}x); targeted TA requested for "
                    f"E&S/MRV capacity building and bankable scaling across {project.region}.{rag_note}"
                )
            else:
                value = (
                    f"{project.project_title} ({project.organization_name}, {project.country}) requests ${project.requested_amount_usd:,.0f} "
                    f"via {self.investor.short_name}'s {eligibility.recommended_instrument}. {project.project_summary} "
                    f"Climate Impact: {ghg_str}; {adap_str}. Aligned with COP31 Antalya commitment ({cop_commit}).{rag_note}"
                )

            # Optional LLM polishing if external provider is configured
            value = self.llm.synthesize_field(
                investor_name=self.investor.name,
                field_label=field.label,
                field_description=field.description,
                applicant_context={
                    "project_title": project.project_title,
                    "organization": project.organization_name,
                    "country": project.country,
                    "sector": project.primary_sector,
                    "requested_usd": project.requested_amount_usd,
                    "ghg_tco2e_yr": project.estimated_ghg_reduction_tco2e_per_year,
                },
                kag_facts=[kg_path] + validating_rules + rules[:3],
                rag_snippets=rag_snippets or [],
                fallback_draft=str(value),
            )

        if validating_rules:
            notes.append(f"KG Validated Rules: {'; '.join(validating_rules)}")

        return FilledFormField(
            field_id=field.field_id,
            label=field.label,
            section=field.section,
            value=value,
            status=status,
            confidence=round(confidence, 2),
            reasoning_mode="KAG",
            evidence_sources=["KAG_KNOWLEDGE_GRAPH", "APPLICANT_PROFILE"],
            kag_reasoning_path=kg_path,
            rag_citations=[s["chunk_id"] for s in (rag_snippets or [])],
            compliance_notes=notes,
        )
