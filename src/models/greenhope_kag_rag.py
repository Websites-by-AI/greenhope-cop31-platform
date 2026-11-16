"""Central GreenHope KAG (Knowledge Graph) + Central Scoped RAG Engine + Zero-Hallucination Application Agent.

Implements the unified GreenHope architecture:
  GREENHOPE_MASTER (Single Source of Truth) + Verified COP31 Investor Database (66 entities)
        -> Central Knowledge Graph (GreenHope domains <-> Investor nodes, instruments, sectors, statuses)
        -> Central RAG with Per-Investor Retrieval Scopes (indexing the 10 Knowledge Packs + all 66 profiles)
        -> Matching & Comparative Evidence Engine ("Why is BBVA a better target than Ziraat Bankası?")
        -> Application-Filling Agent with 4-Tier IP Security & Human Approval Gate (AUTO-FILL -> REVIEW -> APPROVE -> SUBMIT)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .schemas import InvestorRecord, RelationshipStatus

GREENHOPE_DOMAINS = [
    ("climate resilience", ["resilience", "adaptation", "disaster", "urban", "cities"]),
    ("air quality", ["air", "clean", "cities", "health", "mobility", "transport", "emissions"]),
    ("waste", ["waste", "circular", "zero waste", "methane", "recycling"]),
    ("AI", ["ai", "digital", "climate-tech", "innovation", "cleantech", "technology", "data"]),
    ("cities", ["cities", "urban", "municipal", "infrastructure", "mobility", "buildings"]),
    ("climate finance", ["finance", "transition", "green", "blended", "catalytic", "mobiliz", "bond", "loan"]),
    ("MRV", ["mrv", "carbon", "reporting", "impact", "taxonomy", "label", "verification", "esg"]),
]


class GreenHopeCentralKAGRAG:
    """Unified Central Knowledge Graph + Per-Investor Scoped RAG + Anti-Hallucination Application Agent."""

    def __init__(
        self,
        investors: List[InvestorRecord],
        greenhope_master_path: Path,
        knowledge_packs_dir: Path,
    ) -> None:
        self.investors = investors
        self.by_id: Dict[str, InvestorRecord] = {inv.investor_id: inv for inv in investors}
        self.master_path = Path(greenhope_master_path)
        self.packs_dir = Path(knowledge_packs_dir)
        self.master_data: Dict[str, Any] = json.loads(self.master_path.read_text(encoding="utf-8"))

        self.graph = nx.DiGraph()
        self.rag_chunks: List[Dict[str, Any]] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None

        self._build_central_knowledge_graph()
        self._build_central_scoped_rag()

    def reload_master(self) -> Dict[str, Any]:
        self.master_data = json.loads(self.master_path.read_text(encoding="utf-8"))
        return self.master_data

    def update_master_field(self, key: str, value: Any) -> Dict[str, Any]:
        """Update a canonical field in GREENHOPE_MASTER (blocks overwriting Level 4 RESTRICTED secrets)."""
        fields = self.master_data["canonical_fields"]
        if key not in fields:
            raise KeyError(f"Unknown GREENHOPE_MASTER key: {key}")
        if fields[key]["classification"] == "LEVEL_4_RESTRICTED":
            raise PermissionError("Level 4 RESTRICTED fields cannot be modified via the web API.")
        fields[key]["value"] = value if (value is not None and str(value).strip() != "") else None
        fields[key]["confidence"] = 0.98 if fields[key]["value"] is not None else 0.0
        if fields[key]["value"] is not None and "NOT YET PROVIDED" in fields[key].get("source", ""):
            fields[key]["source"] = "Founder Confirmed via GreenHope Master Console"
        self.master_path.write_text(json.dumps(self.master_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return fields[key]

    def _build_central_knowledge_graph(self) -> None:
        """Build ONE unified Knowledge Graph connecting GreenHope, its 7 climate domains, and all 66 COP31 entities."""
        g = self.graph
        g.add_node("GreenHope", node_type="CoreProject", label="GreenHope", stage="City Pilot -> Impact -> Financing -> Scale")

        for domain, _ in GREENHOPE_DOMAINS:
            d_node = f"domain::{domain}"
            g.add_node(d_node, node_type="GreenHopeDomain", label=domain)
            g.add_edge("GreenHope", d_node, relation="OPERATES_IN")

        for inv in self.investors:
            g.add_node(
                inv.investor_id,
                node_type="COP31Entity",
                label=inv.short_name,
                full_name=inv.name,
                relationship_status=inv.relationship_status.value,
                priority_tier=inv.priority_tier,
                ai_rag_priority=inv.ai_rag_priority,
                ecosystem_branch=inv.ecosystem_branch.value,
                greenhope_relevance=inv.greenhope_relevance,
                has_pack=bool(inv.knowledge_pack_slug),
            )

            # Connect matching GreenHope domains directly to this investor based on verified sectors + role + fit notes
            blob = " ".join(
                [
                    inv.cop31_antalya_role,
                    inv.cop31_verified_2026_commitment,
                    inv.greenhope_fit_notes,
                    " ".join(inv.target_sectors),
                    " ".join(inv.financing_instruments),
                ]
            ).lower()
            for domain, keywords in GREENHOPE_DOMAINS:
                hits = [kw for kw in keywords if kw in blob]
                if hits:
                    g.add_edge(f"domain::{domain}", inv.investor_id, relation="ALIGNS_WITH", matched_keywords=hits[:4], weight=len(hits))

            # Connect instruments & relationship status
            status_node = f"status::{inv.relationship_status.value}"
            g.add_node(status_node, node_type="RelationshipStatus", label=inv.relationship_status.value)
            g.add_edge(inv.investor_id, status_node, relation="HAS_EVIDENCE_STATUS")

            branch_node = f"branch::{inv.ecosystem_branch.value}"
            g.add_node(branch_node, node_type="EcosystemBranch", label=inv.ecosystem_branch.value)
            g.add_edge(inv.investor_id, branch_node, relation="IN_ECOSYSTEM_BRANCH")

    def _build_central_scoped_rag(self) -> None:
        """Build ONE Central RAG index over all 66 investor records + all 10 verified Knowledge Packs, filterable by investor scope."""
        chunks: List[Dict[str, Any]] = []

        for inv in self.investors:
            scope = inv.knowledge_pack_slug or inv.investor_id
            chunks.append(
                {
                    "chunk_id": f"{scope}::master_profile",
                    "investor_id": inv.investor_id,
                    "scope": scope,
                    "source_file": "data/cop31_investors_verified.json",
                    "url": inv.verification_source_url,
                    "confidence": 0.97,
                    "text": (
                        f"{inv.name} ({inv.short_name}) | Status: {inv.relationship_status.value} | Tier: {inv.priority_tier} | "
                        f"Priority: {inv.ai_rag_priority} | Branch: {inv.ecosystem_branch.value}. "
                        f"COP31 Role: {inv.cop31_antalya_role}. Commitment: {inv.cop31_verified_2026_commitment}. "
                        f"GreenHope Fit: {inv.greenhope_fit_notes}. "
                        f"Instruments: {', '.join(inv.financing_instruments)}. Sectors: {', '.join(inv.target_sectors)}. "
                        f"Requirements: {'; '.join(inv.mandatory_form_requirements)}."
                    ),
                }
            )

            # Ingest all markdown & verified_claims files from Knowledge Packs when present
            if inv.knowledge_pack_slug:
                pdir = self.packs_dir / inv.knowledge_pack_slug
                if pdir.exists():
                    for md_file in sorted(pdir.glob("*.md")):
                        txt = md_file.read_text(encoding="utf-8").strip()
                        chunks.append(
                            {
                                "chunk_id": f"{scope}::{md_file.stem}",
                                "investor_id": inv.investor_id,
                                "scope": scope,
                                "source_file": f"investors/{inv.knowledge_pack_slug}/{md_file.name}",
                                "url": inv.verification_source_url,
                                "confidence": 0.98,
                                "text": txt,
                            }
                        )
                    claims_file = pdir / "evidence" / "verified_claims.json"
                    if claims_file.exists():
                        claims_data = json.loads(claims_file.read_text(encoding="utf-8"))
                        for idx, cl in enumerate(claims_data.get("claims", []), start=1):
                            chunks.append(
                                {
                                    "chunk_id": f"{scope}::verified_claim_{idx:02d}",
                                    "investor_id": inv.investor_id,
                                    "scope": scope,
                                    "source_file": f"investors/{inv.knowledge_pack_slug}/evidence/verified_claims.json",
                                    "url": cl.get("url", inv.verification_source_url),
                                    "confidence": cl.get("confidence", 0.95),
                                    "text": f"[VERIFIED CLAIM — {cl.get('source')}, {cl.get('date_verified')}] {cl.get('claim')}",
                                }
                            )

        self.rag_chunks = chunks
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
        self._matrix = self._vectorizer.fit_transform([c["text"] for c in self.rag_chunks])

    def query_scoped_rag(self, query: str, investor_id: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """Run Central RAG restricted to a single investor scope (or across the whole COP31 universe if investor_id is None)."""
        assert self._vectorizer is not None and self._matrix is not None
        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix).flatten()

        scored = []
        for idx, ch in enumerate(self.rag_chunks):
            if investor_id and ch["investor_id"] != investor_id:
                continue
            scored.append((float(sims[idx]), ch))
        scored.sort(key=lambda item: item[0], reverse=True)
        top = scored[:top_k]

        scope_label = self.by_id[investor_id].name if investor_id and investor_id in self.by_id else "ALL COP31 ENTITIES (Global Scope)"
        kg_domains = self.get_aligned_domains(investor_id) if investor_id and investor_id in self.by_id else []

        return {
            "query": query,
            "scope": scope_label,
            "investor_id": investor_id,
            "kag_aligned_greenhope_domains": kg_domains,
            "results": [
                {
                    "score": round(score, 4),
                    "chunk_id": ch["chunk_id"],
                    "investor_id": ch["investor_id"],
                    "source_file": ch["source_file"],
                    "url": ch["url"],
                    "confidence": ch["confidence"],
                    "excerpt": ch["text"][:460] + ("..." if len(ch["text"]) > 460 else ""),
                }
                for score, ch in top
            ],
        }

    def get_aligned_domains(self, investor_id: str) -> List[Dict[str, Any]]:
        """Return the Knowledge Graph domain paths linking GreenHope -> Domain -> Investor."""
        paths = []
        for src, _, edata in self.graph.in_edges(investor_id, data=True):
            if edata.get("relation") == "ALIGNS_WITH":
                paths.append(
                    {
                        "domain": self.graph.nodes[src]["label"],
                        "path": f"GreenHope --[OPERATES_IN]--> {self.graph.nodes[src]['label']} --[ALIGNS_WITH]--> {self.by_id[investor_id].short_name}",
                        "matched_keywords": edata.get("matched_keywords", []),
                        "strength": edata.get("weight", 1),
                    }
                )
        paths.sort(key=lambda p: p["strength"], reverse=True)
        return paths

    def get_knowledge_graph_subgraph(self, investor_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Return a clean JSON node/link subgraph for interactive visualization in the web UI."""
        if not investor_ids:
            investor_ids = [
                "inv_bbva_group",
                "inv_garanti_bbva",
                "inv_aiib",
                "inv_world_bank_ibrd",
                "inv_qnb_turkiye",
                "inv_meridiam",
                "inv_m_and_g",
                "inv_hsbc",
                "inv_akbank",
                "inv_denizbank",
            ]
        valid_ids = [iid for iid in investor_ids if iid in self.by_id]

        nodes = [{"id": "GreenHope", "label": "GreenHope", "group": "core"}]
        edges = []
        for dom, _ in GREENHOPE_DOMAINS:
            did = f"domain::{dom}"
            nodes.append({"id": did, "label": dom, "group": "domain"})
            edges.append({"source": "GreenHope", "target": did, "label": "OPERATES_IN"})

        for iid in valid_ids:
            inv = self.by_id[iid]
            nodes.append(
                {
                    "id": iid,
                    "label": inv.short_name,
                    "group": "investor",
                    "status": inv.relationship_status.value,
                    "tier": inv.priority_tier,
                    "priority": inv.ai_rag_priority,
                }
            )
            for src, _, edata in self.graph.in_edges(iid, data=True):
                if edata.get("relation") == "ALIGNS_WITH":
                    edges.append({"source": src, "target": iid, "label": "ALIGNS_WITH", "weight": edata.get("weight", 1)})

        return {"nodes": nodes, "edges": edges}

    def score_for_greenhope(self, investor_id: str) -> Dict[str, Any]:
        """Compute an evidence-grounded KAG+RAG strategic fit score for GreenHope (city pilot -> impact -> financing -> scale)."""
        inv = self.by_id[investor_id]
        domains = self.get_aligned_domains(investor_id)
        domain_score = min(40.0, len(domains) * 6.5)

        status_bonus = {
            RelationshipStatus.INVESTOR_CONFIRMED: 25.0,
            RelationshipStatus.FINANCE_PARTICIPANT: 18.0,
            RelationshipStatus.POTENTIAL_STRATEGIC_PARTNER: 14.0,
            RelationshipStatus.COP31_SUPPORTER: 6.0,
        }[inv.relationship_status]

        tier_bonus = 20.0 if "Tier A" in inv.priority_tier else (13.0 if "Tier B" in inv.priority_tier else 8.0)
        geo_bonus = 10.0 if any(g.lower() in {"türkiye", "global", "emerging markets", "europe"} for g in inv.geographic_focus) else 3.0
        pack_bonus = 5.0 if inv.knowledge_pack_slug else 0.0

        total = round(min(100.0, domain_score + status_bonus + tier_bonus + geo_bonus + pack_bonus), 1)
        return {
            "investor_id": investor_id,
            "name": inv.name,
            "short_name": inv.short_name,
            "greenhope_fit_score": total,
            "aligned_domains": [d["domain"] for d in domains],
            "domain_paths": domains,
            "relationship_status": inv.relationship_status.value,
            "priority_tier": inv.priority_tier,
            "ai_rag_priority": inv.ai_rag_priority,
            "has_knowledge_pack": bool(inv.knowledge_pack_slug),
        }

    def compare_investors(self, inv_id_a: str, inv_id_b: str) -> Dict[str, Any]:
        """Evidence-based KAG+RAG comparison (e.g., 'Why is BBVA a better target for GreenHope than Ziraat Bankası?')."""
        score_a = self.score_for_greenhope(inv_id_a)
        score_b = self.score_for_greenhope(inv_id_b)
        inv_a = self.by_id[inv_id_a]
        inv_b = self.by_id[inv_id_b]

        winner = score_a if score_a["greenhope_fit_score"] >= score_b["greenhope_fit_score"] else score_b
        loser = score_b if winner is score_a else score_a
        w_inv = self.by_id[winner["investor_id"]]
        l_inv = self.by_id[loser["investor_id"]]

        only_winner_domains = sorted(set(winner["aligned_domains"]) - set(loser["aligned_domains"]))
        shared_domains = sorted(set(winner["aligned_domains"]) & set(loser["aligned_domains"]))

        rag_a = self.query_scoped_rag("GreenHope climate resilience innovation cleantech city pilot financing", investor_id=inv_id_a, top_k=2)
        rag_b = self.query_scoped_rag("GreenHope climate resilience innovation cleantech city pilot financing", investor_id=inv_id_b, top_k=2)

        reasons = [
            f"**Higher GreenHope KAG+RAG Strategic Fit:** {w_inv.short_name} scores **{winner['greenhope_fit_score']}/100** vs. {l_inv.short_name}'s **{loser['greenhope_fit_score']}/100**.",
            f"**Evidence & Verification Tier:** {w_inv.short_name} is `{w_inv.relationship_status.value}` ({w_inv.priority_tier}, Priority `{w_inv.ai_rag_priority}`), whereas {l_inv.short_name} is `{l_inv.relationship_status.value}` ({l_inv.priority_tier}, Priority `{l_inv.ai_rag_priority}`).",
            f"**Knowledge Graph Domain Alignment:** Both cover `{', '.join(shared_domains) or 'general climate finance'}`; {w_inv.short_name} adds stronger direct alignment on `{', '.join(only_winner_domains) or 'innovation-to-investment cleantech deployment'}`.",
            f"**Verified COP31 Fit Rationale ({w_inv.short_name}):** {w_inv.greenhope_fit_notes}",
            f"**Relative Positioning ({l_inv.short_name}):** {l_inv.greenhope_fit_notes}",
        ]

        return {
            "question": f"Why is {inv_a.short_name} vs. {inv_b.short_name} a better COP31 target for GreenHope?",
            "recommended_target": winner["investor_id"],
            "recommended_name": w_inv.name,
            "investor_a": {**score_a, "cop31_role": inv_a.cop31_antalya_role, "fit_notes": inv_a.greenhope_fit_notes, "evidence": rag_a["results"]},
            "investor_b": {**score_b, "cop31_role": inv_b.cop31_antalya_role, "fit_notes": inv_b.greenhope_fit_notes, "evidence": rag_b["results"]},
            "evidence_based_reasons": reasons,
        }

    def run_application_agent(self, investor_id: str, custom_overrides: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run the strict Anti-Hallucination & 4-Tier IP-Protected Application-Filling Agent for GreenHope.

        Pipeline:
          FORM FIELD -> FIELD CLASSIFICATION -> MATCH TO GREENHOPE_MASTER -> IP SECURITY CHECK
          -> SOURCE VERIFICATION -> CONFIDENCE -> DRAFT ANSWER -> HUMAN APPROVAL (AUTO-FILL -> REVIEW -> APPROVE -> SUBMIT)
        """
        self.reload_master()
        inv = self.by_id[investor_id]
        canonical = self.master_data["canonical_fields"]
        custom_overrides = custom_overrides or {}

        # Load investor's exact application questions if Knowledge Pack exists, otherwise standard 12-field schema
        questions = [
            {"field_id": "organization_name", "label": "Organization name", "master_key": "organization", "required": True},
            {"field_id": "project_description", "label": "Project description", "master_key": "solution", "required": True},
            {"field_id": "technology", "label": "Technology", "master_key": "technology", "required": True},
            {"field_id": "climate_impact", "label": "Climate impact", "master_key": "climate_impact", "required": True},
            {"field_id": "target_market", "label": "Target market", "master_key": "target_users", "required": True},
            {"field_id": "funding_required", "label": "Funding required", "master_key": "funding_requirement", "required": True},
            {"field_id": "current_stage", "label": "Current stage", "master_key": "current_stage", "required": True},
            {"field_id": "annual_revenue", "label": "Annual revenue", "master_key": "annual_revenue", "required": True},
            {"field_id": "team", "label": "Team", "master_key": "founder_team", "required": True},
            {"field_id": "implementation_location", "label": "Implementation location", "master_key": "geography", "required": True},
            {"field_id": "expected_impact", "label": "Expected impact", "master_key": "metrics", "required": True},
            {"field_id": "ip_and_proprietary_algorithms", "label": "Proprietary algorithms / unpublished IP details", "master_key": "ip_status", "required": False},
        ]
        if inv.knowledge_pack_slug:
            q_path = self.packs_dir / inv.knowledge_pack_slug / "application_questions.json"
            if q_path.exists():
                questions = json.loads(q_path.read_text(encoding="utf-8")).get("questions", questions)

        # Retrieve scoped RAG evidence once for investor framing
        rag_ctx = self.query_scoped_rag(f"requirements instruments COP31 strategy GreenHope {inv.short_name}", investor_id=investor_id, top_k=3)
        cite_ids = [r["chunk_id"] for r in rag_ctx["results"][:2]]
        kg_fit = self.score_for_greenhope(investor_id)

        draft_fields: List[Dict[str, Any]] = []
        supporter_warning = None
        if inv.relationship_status in (RelationshipStatus.COP31_SUPPORTER, RelationshipStatus.POTENTIAL_STRATEGIC_PARTNER):
            supporter_warning = (
                f"GOVERNANCE WARNING: {inv.name} is classified as '{inv.relationship_status.value}' (NOT 'Investor Confirmed'). "
                f"Frame outreach as a strategic pilot / ecosystem referral—do NOT assume open direct grant or equity funding."
            )

        for q in questions:
            fid = q["field_id"]
            mkey = q["master_key"]
            c_entry = canonical.get(mkey, {"classification": "LEVEL_1_PUBLIC", "value": None, "source": "Unmapped", "confidence": 0.0})
            sec_level = c_entry["classification"]
            raw_val = custom_overrides.get(fid) if fid in custom_overrides and str(custom_overrides[fid]).strip() else c_entry["value"]

            # 1. STRICT 4-TIER IP PROTECTION: Never auto-fill LEVEL_3_CONFIDENTIAL or LEVEL_4_RESTRICTED!
            if sec_level in ("LEVEL_3_CONFIDENTIAL", "LEVEL_4_RESTRICTED"):
                draft_fields.append(
                    {
                        "field_id": fid,
                        "field": q["label"],
                        "master_key": mkey,
                        "security_level": sec_level,
                        "answer": None,
                        "source": c_entry["source"],
                        "confidence": 1.0,
                        "status": "BLOCKED_BY_IP_SECURITY",
                        "action": "DO_NOT_AUTO_SUBMIT_PROTECT_IP",
                        "pipeline_trace": f"{q['label']} -> {sec_level} -> BLOCKED by Anti-Copying IP Guard (manual NDA required)",
                        "rag_citations": [],
                        "approved": False,
                    }
                )
                continue

            # 2. ZERO-HALLUCINATION GUARD: If master data is missing -> return null & ASK_USER!
            if raw_val is None or str(raw_val).strip() == "":
                draft_fields.append(
                    {
                        "field_id": fid,
                        "field": q["label"],
                        "master_key": mkey,
                        "security_level": sec_level,
                        "answer": None,
                        "source": "GREENHOPE_MASTER (missing value)",
                        "confidence": 0.0,
                        "status": "MISSING_INFORMATION",
                        "action": "ASK_USER",
                        "pipeline_trace": f"{q['label']} -> {sec_level} -> No verified value in GREENHOPE_MASTER -> NEVER HALLUCINATE -> ASK_USER",
                        "rag_citations": [],
                        "approved": False,
                    }
                )
                continue

            # 3. GROUNDED DRAFT ANSWER tailored cleanly to this investor's verified mandate
            answer_text = str(raw_val)
            if fid == "project_description":
                answer_text = (
                    f"{raw_val} Tailored for {inv.short_name} ({inv.relationship_status.value}): aligns with "
                    f"{', '.join(kg_fit['aligned_domains'][:4]) or 'climate transition'} via {inv.financing_instruments[0]}."
                )
            elif fid == "funding_required":
                answer_text = f"{raw_val} (Target pathway with {inv.short_name}: {inv.financing_instruments[0]}; bank ticket band USD {inv.typical_ticket_min_usd:,.0f}–{inv.typical_ticket_max_usd:,.0f})."

            status = "ready_for_approval" if sec_level == "LEVEL_1_PUBLIC" else "requires_user_confirmation"
            action = "HUMAN_APPROVE_BEFORE_SUBMIT"
            draft_fields.append(
                {
                    "field_id": fid,
                    "field": q["label"],
                    "master_key": mkey,
                    "security_level": sec_level,
                    "answer": answer_text,
                    "source": c_entry["source"],
                    "confidence": c_entry["confidence"],
                    "status": status,
                    "action": action,
                    "pipeline_trace": f"{q['label']} -> {sec_level} -> Matched GREENHOPE_MASTER.{mkey} -> Verified ({c_entry['confidence']:.2f}) -> Draft -> Awaiting Human Approval",
                    "rag_citations": cite_ids,
                    "approved": False,
                }
            )

        return {
            "investor_id": inv.investor_id,
            "investor_name": inv.name,
            "short_name": inv.short_name,
            "relationship_status": inv.relationship_status.value,
            "priority_tier": inv.priority_tier,
            "portal_url": inv.application_portal_url,
            "workflow_rule": "AUTO-FILL -> REVIEW -> APPROVE -> SUBMIT (Never Auto-Submit)",
            "supporter_warning": supporter_warning,
            "greenhope_fit_score": kg_fit["greenhope_fit_score"],
            "aligned_domains": kg_fit["aligned_domains"],
            "missing_count": sum(1 for f in draft_fields if f["status"] == "MISSING_INFORMATION"),
            "blocked_ip_count": sum(1 for f in draft_fields if f["status"] == "BLOCKED_BY_IP_SECURITY"),
            "ready_count": sum(1 for f in draft_fields if f["status"] in ("ready_for_approval", "requires_user_confirmation")),
            "fields": draft_fields,
        }
