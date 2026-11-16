"""Hybrid KAG + RAG engine combining deterministic Knowledge Graph reasoning with cited RAG narrative grounding.

Ideal for blended-finance DFIs, MDBs, and catalytic platforms where:
- KAG enforces hard constraints (geography, sector, ticket bounds, exclusion lists, NDA/Paris/IFC/Shariah rules)
- RAG retrieves policy chunks, COP31 commitment language, and form field instructions for cited narrative answers
"""

from __future__ import annotations

from typing import Optional

from ..security.tenant_guard import TenantIsolationGuard
from .kag_engine import InvestorKAGEngine
from .llm_adapter import GroundedLLMAdapter
from .rag_engine import InvestorRAGEngine
from .schemas import (
    ApplicantProject,
    EligibilityEvaluation,
    FilledFormField,
    FormFieldSpec,
    InvestorRecord,
)


class InvestorHybridKAGRAGEngine:
    """Combines per-investor KAG Knowledge Graph reasoning with per-investor RAG retrieval."""

    def __init__(
        self,
        investor: InvestorRecord,
        kag: InvestorKAGEngine,
        rag: InvestorRAGEngine,
        tenant_guard: Optional[TenantIsolationGuard] = None,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> None:
        if tenant_guard is not None:
            tenant_guard.assert_investor_match(investor.investor_id)
        self.investor = investor
        self.kag = kag
        self.rag = rag
        self.tenant_guard = tenant_guard
        self.llm = llm_adapter or GroundedLLMAdapter()

    def evaluate_eligibility(self, project: ApplicantProject) -> EligibilityEvaluation:
        # KAG provides deterministic multi-hop rule verification as source of truth
        return self.kag.evaluate_eligibility(project)

    def fill_field(
        self,
        field: FormFieldSpec,
        project: ApplicantProject,
        eligibility: EligibilityEvaluation,
    ) -> FilledFormField:
        """Route hard rules to KAG, narrative sections to RAG+KAG fusion, preserving both provenance traces."""
        query = f"{field.label} {field.description} {' '.join(field.expected_keywords)} {project.primary_sector} {project.country}"
        rag_snippets = self.rag.retrieve(query, top_k=3)

        if field.generation_strategy in {"KAG_RULE", "APPLICANT_DIRECT"}:
            filled = self.kag.fill_field(field, project, eligibility, rag_snippets=rag_snippets[:1])
            filled.reasoning_mode = "HYBRID_KAG_RAG (KAG-primary)"
            filled.evidence_sources = ["KAG_KNOWLEDGE_GRAPH", "RAG_VECTOR_CORPUS", "APPLICANT_PROFILE"]
            return filled

        if field.generation_strategy == "RAG_NARRATIVE":
            filled = self.rag.fill_field(field, project, eligibility)
            filled.reasoning_mode = "HYBRID_KAG_RAG (RAG-primary)"
            filled.kag_reasoning_path = (
                f"{self.investor.investor_id} --[USES_FORM_TEMPLATE]--> form::{self.investor.form_template_type.value} "
                f"--[HAS_FORM_FIELD]--> field::{field.field_id}"
            )
            filled.evidence_sources = ["RAG_VECTOR_CORPUS", "KAG_KNOWLEDGE_GRAPH", "APPLICANT_PROFILE"]
            return filled

        # Full HYBRID fusion: KAG logical structure enriched with RAG citations
        filled = self.kag.fill_field(field, project, eligibility, rag_snippets=rag_snippets)
        filled.reasoning_mode = "HYBRID_KAG_RAG"
        filled.evidence_sources = ["KAG_KNOWLEDGE_GRAPH", "RAG_VECTOR_CORPUS", "APPLICANT_PROFILE"]
        filled.confidence = round(min(0.97, filled.confidence + 0.03), 2)
        return filled
