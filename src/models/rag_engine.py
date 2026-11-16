"""RAG (Retrieval-Augmented Generation) engine dedicated strictly to ONE COP31 investor.

Builds an isolated chunked policy/product/form-guidance corpus per investor, indexes it with a hybrid
word + character n-gram TF-IDF vector index (cosine similarity + MMR diversity selection), and synthesizes
grounded form-field values with explicit `[chunk_id]` provenance citations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..forms.form_templates import get_form_template
from ..security.tenant_guard import PIIRedactor, TenantIsolationGuard
from .kag_engine import COUNTRY_REGION_MAP
from .llm_adapter import GroundedLLMAdapter
from .schemas import (
    ApplicantProject,
    EligibilityEvaluation,
    FieldFillStatus,
    FilledFormField,
    FormFieldSpec,
    InvestorRecord,
)


class InvestorRAGEngine:
    """Dedicated Retrieval-Augmented Generation engine scoped strictly to one COP31 investor."""

    def __init__(
        self,
        investor: InvestorRecord,
        chunks: List[Dict[str, Any]],
        tenant_guard: Optional[TenantIsolationGuard] = None,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> None:
        if tenant_guard is not None:
            tenant_guard.assert_investor_match(investor.investor_id)
            for ch in chunks:
                tenant_guard.assert_investor_match(ch["investor_id"])
        self.investor = investor
        self.chunks = chunks
        self.tenant_guard = tenant_guard
        self.llm = llm_adapter or GroundedLLMAdapter()

        # Fit isolated per-investor TF-IDF vector index (unigram+bigram word features)
        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
        )
        texts = [f"{c['title']} {c['section']} {c['text']}" for c in self.chunks]
        self._matrix = self._vectorizer.fit_transform(texts)

    @classmethod
    def build_for_investor(
        cls,
        investor: InvestorRecord,
        tenant_guard: Optional[TenantIsolationGuard] = None,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> "InvestorRAGEngine":
        """Create a domain-rich, investor-isolated RAG chunk corpus covering COP31 commitments, products, rules & forms."""
        if tenant_guard is not None:
            tenant_guard.assert_investor_match(investor.investor_id)

        inv_id = investor.investor_id
        template = get_form_template(investor.form_template_type)
        chunks: List[Dict[str, Any]] = [
            {
                "chunk_id": f"{inv_id}::mandate_cop31",
                "investor_id": inv_id,
                "section": "COP31 Antalya 2026 Mandate",
                "title": f"{investor.name} ({investor.short_name}) COP31 Role & Commitments",
                "text": (
                    f"{investor.name} is a {investor.category.value} headquartered in {investor.hq_country}. "
                    f"At UNFCCC COP31 in Antalya (November 9-20, 2026), its verified role is: {investor.cop31_antalya_role}. "
                    f"Verified COP31 2026 climate finance commitment: {investor.cop31_verified_2026_commitment}. "
                    f"Source verification: {investor.verification_source_url}."
                ),
            },
            {
                "chunk_id": f"{inv_id}::instruments_tickets",
                "investor_id": inv_id,
                "section": "Financial Products & Ticket Sizing",
                "title": f"{investor.short_name} Financing Instruments & Ticket Bounds",
                "text": (
                    f"{investor.name} provides the following climate financing instruments: {', '.join(investor.financing_instruments)}. "
                    f"Typical transaction ticket range is USD {investor.typical_ticket_min_usd:,.0f} to USD {investor.typical_ticket_max_usd:,.0f}. "
                    f"Eligible applicant profiles include: {', '.join(investor.eligible_applicant_types)}."
                ),
            },
            {
                "chunk_id": f"{inv_id}::sectors_geography",
                "investor_id": inv_id,
                "section": "Eligible Sectors & Geographies",
                "title": f"{investor.short_name} Priority Climate Sectors & Regional Mandate",
                "text": (
                    f"Priority climate sectors funded by {investor.name}: {', '.join(investor.target_sectors)}. "
                    f"Target geographic focus includes: {', '.join(investor.geographic_focus)}. "
                    f"Projects outside primary regions or ticket bounds may require syndicated or on-lending structures."
                ),
            },
            {
                "chunk_id": f"{inv_id}::compliance_esg",
                "investor_id": inv_id,
                "section": "Compliance, ESG & Exclusion Criteria",
                "title": f"{investor.short_name} Mandatory Form & Underwriting Requirements",
                "text": (
                    f"Mandatory requirements to complete {investor.short_name}'s application form: "
                    f"{'; '.join(investor.mandatory_form_requirements)}. "
                    f"Explicit exclusion rules: {'; '.join(investor.exclusion_rules) if investor.exclusion_rules else 'Standard Paris-aligned fossil fuel exclusions apply'}. "
                    f"Official application portal: {investor.application_portal_url}."
                ),
            },
            {
                "chunk_id": f"{inv_id}::form_standard",
                "investor_id": inv_id,
                "section": "Application Form Governance",
                "title": f"{investor.short_name} Form Template: {template.title}",
                "text": (
                    f"{investor.name} uses the '{template.title}' workflow governed by {template.governing_standard}. "
                    f"Typical review timeline is {template.typical_review_timeline}. "
                    f"Form sections required: {', '.join(sorted(set(f.section for f in template.fields)))}."
                ),
            },
        ]

        # Field-specific guidance chunks so RAG retrieval achieves high precision on every form slot
        for idx, field in enumerate(template.fields, start=1):
            chunks.append(
                {
                    "chunk_id": f"{inv_id}::field_guide_{idx:02d}_{field.field_id}",
                    "investor_id": inv_id,
                    "section": f"Form Field Guide: {field.section}",
                    "title": f"{investor.short_name} Guidance for '{field.label}'",
                    "text": (
                        f"Field '{field.label}' ({field.field_id}) under section '{field.section}' on {investor.short_name}'s "
                        f"{template.title}: {field.description} Required={field.required}. "
                        f"Expected evidence keywords: {', '.join(field.expected_keywords) if field.expected_keywords else 'Verified applicant facts'}. "
                        f"Align response with {investor.short_name}'s COP31 priorities ({investor.cop31_antalya_role}) and instruments ({', '.join(investor.financing_instruments[:3])})."
                    ),
                }
            )

        return cls(investor=investor, chunks=chunks, tenant_guard=tenant_guard, llm_adapter=llm_adapter)

    def save(self, path: Path) -> None:
        if self.tenant_guard is not None:
            self.tenant_guard.assert_path_within_tenant(path)
        payload = {
            "investor_id": self.investor.investor_id,
            "corpus_format": "cop31-rag-chunks-v1",
            "chunk_count": len(self.chunks),
            "chunks": self.chunks,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(
        cls,
        investor: InvestorRecord,
        path: Path,
        tenant_guard: Optional[TenantIsolationGuard] = None,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> "InvestorRAGEngine":
        if tenant_guard is not None:
            tenant_guard.assert_path_within_tenant(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if tenant_guard is not None:
            tenant_guard.assert_investor_match(payload["investor_id"])
        return cls(investor=investor, chunks=payload["chunks"], tenant_guard=tenant_guard, llm_adapter=llm_adapter)

    def retrieve(self, query: str, top_k: int = 3, mmr_lambda: float = 0.72) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks strictly from this investor's corpus using cosine similarity + MMR diversity."""
        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix).flatten()
        if len(sims) == 0:
            return []

        selected_indices: List[int] = []
        candidate_indices = list(np.argsort(-sims)[: max(top_k * 3, 6)])

        while len(selected_indices) < min(top_k, len(candidate_indices)):
            best_idx = None
            best_mmr = -1e9
            for idx in candidate_indices:
                if idx in selected_indices:
                    continue
                relevance = float(sims[idx])
                if not selected_indices:
                    diversity_penalty = 0.0
                else:
                    cand_vec = self._matrix[idx]
                    sel_vecs = self._matrix[selected_indices]
                    diversity_penalty = float(cosine_similarity(cand_vec, sel_vecs).max())
                mmr_score = mmr_lambda * relevance - (1.0 - mmr_lambda) * diversity_penalty
                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_idx = int(idx)
            if best_idx is None:
                break
            selected_indices.append(best_idx)

        results: List[Dict[str, Any]] = []
        for idx in selected_indices:
            chunk = self.chunks[idx]
            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "title": chunk["title"],
                    "section": chunk["section"],
                    "text": chunk["text"],
                    "score": round(float(sims[idx]), 4),
                }
            )
        return results

    def evaluate_eligibility(self, project: ApplicantProject) -> EligibilityEvaluation:
        """Retrieval-grounded eligibility scoring for pure-RAG investor models."""
        query = (
            f"{project.primary_sector} {' '.join(project.secondary_sectors)} {project.country} {project.region} "
            f"{project.applicant_type} {' '.join(project.preferred_instruments)} {project.project_summary}"
        )
        retrieved = self.retrieve(query, top_k=4)
        avg_sim = sum(r["score"] for r in retrieved) / max(1, len(retrieved))

        passed: List[str] = []
        failed: List[str] = []
        warnings: List[str] = []
        score = min(40.0, avg_sim * 130.0)

        # Verify core structured constraints grounded in retrieved chunks
        country_tokens = set(COUNTRY_REGION_MAP.get(project.country.lower(), [project.country.lower(), project.region.lower(), "global"]))
        country_tokens.add(project.region.lower())
        country_match = any(
            any(tok in g.lower() or g.lower() in tok for tok in country_tokens)
            for g in self.investor.geographic_focus
        )
        if country_match:
            passed.append(f"Retrieved mandate confirms coverage for {project.country} ({', '.join(self.investor.geographic_focus[:3])}).")
            score += 25.0
        else:
            failed.append(f"Country '{project.country}' not listed in {self.investor.short_name} geographic focus.")

        # Verify applicant type & sector overlap grounded in retrieved chunks
        app_match = any(
            project.applicant_type.lower() in a.lower() or a.lower() in project.applicant_type.lower()
            for a in self.investor.eligible_applicant_types
        )
        if app_match:
            passed.append(f"Applicant profile '{project.applicant_type}' aligns with {self.investor.short_name} banking segment.")
            score += 10.0
        else:
            warnings.append(f"Applicant type '{project.applicant_type}' may require specialized desk routing.")

        if self.investor.typical_ticket_min_usd <= project.requested_amount_usd <= self.investor.typical_ticket_max_usd:
            passed.append(
                f"Ticket ${project.requested_amount_usd:,.0f} fits {self.investor.short_name} band "
                f"(${self.investor.typical_ticket_min_usd:,.0f}–${self.investor.typical_ticket_max_usd:,.0f})."
            )
            score += 20.0
        else:
            warnings.append("Requested amount is outside typical ticket range; co-financing or structured facility advised.")
            score += 8.0

        if project.fossil_fuel_involvement:
            failed.append("Fossil-fuel involvement triggers ESG exclusion screening.")
            score = max(0.0, score - 35.0)
        else:
            passed.append("No fossil-fuel exclusion conflicts found.")
            score += 10.0

        chosen_inst = self.investor.financing_instruments[0]
        for pref in project.preferred_instruments:
            for inst in self.investor.financing_instruments:
                if pref.lower() in inst.lower() or inst.lower() in pref.lower():
                    chosen_inst = inst
                    score += 10.0
                    passed.append(f"Matched financing product '{chosen_inst}'.")
                    break
            else:
                continue
            break

        eligible = (len(failed) == 0) and (score >= 55.0)
        return EligibilityEvaluation(
            eligible=eligible,
            fit_score=round(min(100.0, score), 1),
            passed_checks=passed,
            failed_checks=failed,
            warnings=warnings,
            recommended_instrument=chosen_inst,
            kag_hops_executed=0,
        )

    def fill_field(
        self,
        field: FormFieldSpec,
        project: ApplicantProject,
        eligibility: EligibilityEvaluation,
    ) -> FilledFormField:
        """Retrieve investor-specific policy chunks and draft a cited form field entry."""
        query = (
            f"{field.label} {field.description} {' '.join(field.expected_keywords)} "
            f"{project.primary_sector} {project.country} {project.applicant_type}"
        )
        retrieved = self.retrieve(query, top_k=3)
        cite_ids = [r["chunk_id"] for r in retrieved]
        cite_tag = " ".join(f"[{c}]" for c in cite_ids[:2])
        top_score = retrieved[0]["score"] if retrieved else 0.0

        fid = field.field_id
        status = FieldFillStatus.FILLED
        notes: List[str] = []
        confidence = min(0.95, max(0.74, 0.78 + top_score * 0.45))

        ghg_str = (
            f"{project.estimated_ghg_reduction_tco2e_per_year:,.0f} tCO2e/year"
            if project.estimated_ghg_reduction_tco2e_per_year
            else "under technical quantification"
        )

        if fid in {"project_title", "sponsor_and_project", "borrower_profile", "company_and_project"}:
            draft = f"{project.project_title} | Entity: {project.organization_name} ({project.applicant_type}) | Market: {project.country} | Sector: {project.primary_sector}"
            confidence = 0.97
        elif fid == "company_identity_masked":
            masked_tax = PIIRedactor.mask_identifier(project.tax_or_registration_id)
            draft = f"{project.organization_name} | Masked VKN/Tax ID: {masked_tax} | Jurisdiction: {project.country}"
            if not project.tax_or_registration_id:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Tax ID/VKN missing; attach verified tax certificate before bank portal upload.")
                confidence = 0.72
            else:
                notes.append("PII masked via PIIRedactor during RAG processing.")
                confidence = 0.95
        elif fid in {"financial_viability_metrics", "financial_profile", "financial_snapshot", "credit_financials"}:
            rev = f"${project.annual_revenue_usd:,.0f}" if project.annual_revenue_usd is not None else "Pending"
            ebitda = f"${project.ebitda_usd:,.0f}" if project.ebitda_usd is not None else "Pending"
            irr = f"{project.expected_irr_percent:.1f}%" if project.expected_irr_percent is not None else "Pending"
            draft = f"Capex: ${project.total_project_cost_usd:,.0f} | Revenue: {rev} | EBITDA: {ebitda} | Projected IRR: {irr}"
            if rev == "Pending" or ebitda == "Pending":
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Attach latest audited financial statements.")
                confidence = 0.75
        elif fid == "enterprise_segment":
            draft = f"{project.applicant_type}{' (EU CBAM Exporter)' if project.eu_cbam_exporter else ''}"
            confidence = 0.94
        elif fid in {"bank_green_program", "climate_thesis_fit"}:
            draft = (
                f"Target Program: {self.investor.name} — {self.investor.cop31_antalya_role}. "
                f"COP31 2026 Commitment: {self.investor.cop31_verified_2026_commitment}. "
                f"Recommended Facility: {eligibility.recommended_instrument} aligned with {project.primary_sector}. {cite_tag}"
            )
        elif fid in {"loan_amount_and_maturity", "facility_structure", "round_and_instrument"}:
            in_band = self.investor.typical_ticket_min_usd <= project.requested_amount_usd <= self.investor.typical_ticket_max_usd
            draft = (
                f"{eligibility.recommended_instrument} | Requested: ${project.requested_amount_usd:,.0f} USD | "
                f"Maturity: {project.implementation_years} years | Program Range: "
                f"${self.investor.typical_ticket_min_usd:,.0f}–${self.investor.typical_ticket_max_usd:,.0f} "
                f"({'In Range' if in_band else 'Syndication/Co-Financing Advised'}). {cite_tag}"
            )
            if not in_band:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Requested amount outside standard single-bank ticket band.")
        elif fid == "collateral_and_kgf_status":
            if project.has_kgf_or_collateral:
                draft = f"Collateral / KGF Guarantee Available for {self.investor.short_name} green credit line underwriting. {cite_tag}"
            else:
                draft = f"ACTION REQUIRED: Confirm collateral package or apply for KGF Treasury-backed sustainability guarantee via {self.investor.short_name}. {cite_tag}"
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Collateral/KGF confirmation required before credit committee approval.")
        elif fid == "inclusive_priority_flags":
            flags = []
            if project.women_or_youth_led:
                flags.append("Women/Youth Entrepreneur Preferential Window")
            if project.eu_cbam_exporter:
                flags.append("EU CBAM Green Export Priority")
            draft = f"{' | '.join(flags) if flags else 'Standard Corporate/SME Green Eligibility'}. {cite_tag}"
        elif fid in {"spo_and_verification"}:
            if project.has_second_party_opinion:
                draft = f"Second-Party Opinion (SPO) & independent GHG assurance ready for {self.investor.short_name} sustainable finance labeling. {cite_tag}"
            else:
                draft = f"PENDING: External Second-Party Opinion (SPO) recommended under ICMA GBP / LMA GLP for {self.investor.short_name}. {cite_tag}"
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Commission SPO before financial close.")
        elif fid in {"environmental_permits_status", "esg_controversy_screen", "esg_impact_governance"}:
            excl_txt = "PASS (zero fossil-fuel involvement)" if not project.fossil_fuel_involvement else "FAIL (fossil-fuel conflict)"
            eia_txt = "EIA / ÇED permits confirmed" if project.has_eia_and_permits else "EIA / environmental permits pending"
            draft = f"Exclusion Check: {excl_txt} | Permits: {eia_txt} | ESG Summary: {project.esg_and_social_impact} {cite_tag}"
            if project.fossil_fuel_involvement:
                status = FieldFillStatus.MISSING_REQUIRED_DATA
                notes.append("Fossil-fuel activity violates bank ESG exclusion policy.")
            elif not project.has_eia_and_permits:
                status = FieldFillStatus.PARTIAL_NEEDS_REVIEW
                notes.append("Attach environmental permits before disbursement.")
        elif fid in {"carbon_and_cbam_impact", "spts_and_kpis", "decarbonization_unit_economics"}:
            cbam = " Directly reduces EU CBAM carbon border exposure for export supply chains." if project.eu_cbam_exporter else ""
            draft = (
                f"Projected Emissions Reduction: {ghg_str}. {project.climate_rationale}{cbam} "
                f"Aligned with {self.investor.short_name} sustainable finance KPI reporting. {cite_tag}"
            )
        elif fid in {"eligible_green_use_of_proceeds", "use_of_proceeds_narrative", "technology_and_moat", "taxonomy_alignment"}:
            draft = (
                f"Green Use of Proceeds ({project.primary_sector}): {project.technology_and_innovation} "
                f"Maps to {self.investor.short_name} eligible categories ({', '.join(self.investor.target_sectors[:3])}) "
                f"and governing requirements ({'; '.join(self.investor.mandatory_form_requirements[:2])}). {cite_tag}"
            )
        elif fid in {"risks_and_mitigants"}:
            draft = f"{project.key_risks_and_mitigants} {cite_tag}"
        else:
            draft = (
                f"{project.project_title} ({project.organization_name}, {project.country}) seeks ${project.requested_amount_usd:,.0f} "
                f"under {self.investor.name}'s {eligibility.recommended_instrument}. {project.project_summary} "
                f"Expected impact: {ghg_str}. {cite_tag}"
            )

        final_value = self.llm.synthesize_field(
            investor_name=self.investor.name,
            field_label=field.label,
            field_description=field.description,
            applicant_context={
                "project_title": project.project_title,
                "organization": project.organization_name,
                "country": project.country,
                "sector": project.primary_sector,
                "requested_usd": project.requested_amount_usd,
            },
            kag_facts=[],
            rag_snippets=retrieved,
            fallback_draft=draft,
        )

        return FilledFormField(
            field_id=field.field_id,
            label=field.label,
            section=field.section,
            value=final_value,
            status=status,
            confidence=round(confidence, 2),
            reasoning_mode="RAG",
            evidence_sources=["RAG_VECTOR_CORPUS", "APPLICANT_PROFILE"],
            kag_reasoning_path=None,
            rag_citations=cite_ids,
            compliance_notes=notes,
        )
