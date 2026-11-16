"""Strict Pydantic v2 schemas for the COP31 Investor Registry, Security Vault, KAG/RAG Models, and Application Forms."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class InvestorCategory(str, Enum):
    MDB = "Multilateral Development Bank (MDB)"
    BILATERAL_DFI = "Bilateral DFI"
    NATIONAL_DEV_BANK = "National Development Bank"
    CLIMATE_FUND = "Multilateral Climate Fund"
    TURKISH_COMMERCIAL_BANK = "Turkish Commercial Bank"
    TURKISH_STATE_BANK = "Turkish State Bank"
    GLOBAL_COMMERCIAL_BANK = "Global Commercial Bank"
    INSTITUTIONAL_CATALYTIC_PE = "Institutional / Catalytic / Climate PE"
    CLIMATE_FINANCE_NETWORK = "Climate Finance Network / Public Facilitator"
    STRATEGIC_CORPORATE_PARTNER = "Strategic Corporate / COP31 Supporter"


class AIModelArchitecture(str, Enum):
    KAG = "KAG"
    RAG = "RAG"
    HYBRID_KAG_RAG = "HYBRID_KAG_RAG"


class FormTemplateType(str, Enum):
    MDB_CONCEPT_NOTE = "MDB_CONCEPT_NOTE"
    CLIMATE_FUND_PROPOSAL = "CLIMATE_FUND_PROPOSAL"
    DFI_PROJECT_INTAKE = "DFI_PROJECT_INTAKE"
    TURKISH_BANK_GREEN_LOAN = "TURKISH_BANK_GREEN_LOAN"
    GLOBAL_COMMERCIAL_BANK_TRANSITION = "GLOBAL_COMMERCIAL_BANK_TRANSITION"
    CATALYTIC_PE_VC_INTAKE = "CATALYTIC_PE_VC_INTAKE"


class SecurityRole(str, Enum):
    ADMIN = "ADMIN"
    SECURITY_OFFICER = "SECURITY_OFFICER"
    MODEL_ENGINEER = "MODEL_ENGINEER"
    FORM_OPERATOR = "FORM_OPERATOR"
    AUDITOR = "AUDITOR"


class FieldFillStatus(str, Enum):
    FILLED = "FILLED"
    PARTIAL_NEEDS_REVIEW = "PARTIAL_NEEDS_REVIEW"
    MISSING_REQUIRED_DATA = "MISSING_REQUIRED_DATA"


class RelationshipStatus(str, Enum):
    INVESTOR_CONFIRMED = "Investor Confirmed"
    FINANCE_PARTICIPANT = "Finance Participant"
    COP31_SUPPORTER = "COP31 Supporter"
    POTENTIAL_STRATEGIC_PARTNER = "Potential Strategic Partner"


class EcosystemBranch(str, Enum):
    COMMERCIAL_BANKS = "Commercial Banks"
    DEVELOPMENT_BANKS = "Development Banks"
    INFRASTRUCTURE_IMPACT_INVESTORS = "Infrastructure / Impact Investors"
    CLIMATE_FINANCE_NETWORKS = "Climate Finance Networks"
    MULTILATERAL_CLIMATE_FUNDS = "Multilateral Climate Funds"
    STRATEGIC_CORPORATE_CAPITAL = "Strategic / Corporate Capital"


class SecurityClassification(str, Enum):
    LEVEL_1_PUBLIC = "LEVEL_1_PUBLIC"
    LEVEL_2_INTERNAL = "LEVEL_2_INTERNAL"
    LEVEL_3_CONFIDENTIAL = "LEVEL_3_CONFIDENTIAL"
    LEVEL_4_RESTRICTED = "LEVEL_4_RESTRICTED"


class InvestorRecord(BaseModel):
    """Verified COP31 Antalya (Nov 2026) Investor / Bank / Finance Ecosystem profile."""

    investor_id: str = Field(..., pattern=r"^inv_[a-z0-9_]+$")
    name: str
    short_name: str
    category: InvestorCategory
    ecosystem_branch: EcosystemBranch = EcosystemBranch.COMMERCIAL_BANKS
    relationship_status: RelationshipStatus = RelationshipStatus.FINANCE_PARTICIPANT
    priority_tier: str = "Tier C — Ecosystem / Strategic"
    ai_rag_priority: str = "P2"  # P1, P2, P3
    greenhope_relevance: str = "High"
    greenhope_fit_notes: str = ""
    knowledge_pack_slug: Optional[str] = None
    hq_country: str
    geographic_focus: List[str]
    cop31_antalya_role: str
    cop31_verified_2026_commitment: str
    financing_instruments: List[str]
    typical_ticket_min_usd: int = Field(..., ge=0)
    typical_ticket_max_usd: int = Field(..., ge=0)
    target_sectors: List[str]
    eligible_applicant_types: List[str]
    application_portal_url: str
    form_template_type: FormTemplateType
    mandatory_form_requirements: List[str]
    exclusion_rules: List[str] = Field(default_factory=list)
    recommended_ai_model_type: AIModelArchitecture
    ai_model_rationale: str
    verification_source_url: str
    verification_date: str = "2026-11-15"
    verification_status: str = "VERIFIED_COP31_ANTALYA_2026"
    confidentiality_tier: str = "RESTRICTED_INTERNAL"

    @field_validator("typical_ticket_max_usd")
    @classmethod
    def check_ticket_range(cls, v: int, info: Any) -> int:
        min_v = info.data.get("typical_ticket_min_usd", 0)
        if v < min_v:
            raise ValueError("typical_ticket_max_usd must be >= typical_ticket_min_usd")
        return v


class FormFieldSpec(BaseModel):
    """Schema for a single field on an investor's application form."""

    field_id: str
    label: str
    section: str
    field_type: str  # text, currency_usd, number, enum, list, narrative, compliance_check
    required: bool = True
    description: str
    generation_strategy: str  # KAG_RULE, RAG_NARRATIVE, HYBRID, APPLICANT_DIRECT
    expected_keywords: List[str] = Field(default_factory=list)
    applicant_source_keys: List[str] = Field(default_factory=list)


class FormTemplate(BaseModel):
    """Complete application form template for an investor category."""

    template_id: FormTemplateType
    title: str
    governing_standard: str
    typical_review_timeline: str
    fields: List[FormFieldSpec]


class ApplicantProject(BaseModel):
    """General-purpose climate applicant / project profile adaptable to all sectors."""

    project_id: str
    project_title: str
    organization_name: str
    applicant_type: str  # Large Corporate, SME, Climate-Tech Startup, Municipality, Project SPV, Sovereign/Government, Financial Intermediary, Accredited Entity/NGO
    country: str
    region: str
    tax_or_registration_id: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    iban_or_account: Optional[str] = None
    primary_sector: str
    secondary_sectors: List[str] = Field(default_factory=list)
    requested_amount_usd: int = Field(..., gt=0)
    total_project_cost_usd: int = Field(..., gt=0)
    co_financing_committed_usd: int = Field(default=0, ge=0)
    preferred_instruments: List[str]
    project_stage: str  # Concept, Feasibility, Ready-to-Build, Scaling/Growth, Operational Expansion
    implementation_years: int = Field(default=3, ge=1, le=25)
    estimated_ghg_reduction_tco2e_per_year: Optional[float] = None
    adaptation_beneficiaries: Optional[int] = None
    annual_revenue_usd: Optional[float] = None
    ebitda_usd: Optional[float] = None
    expected_irr_percent: Optional[float] = None
    has_eia_and_permits: bool = False
    has_paris_alignment_assessment: bool = False
    has_nda_no_objection_letter: bool = False
    has_second_party_opinion: bool = False
    has_kgf_or_collateral: bool = False
    shariah_compliant_structure: bool = False
    women_or_youth_led: bool = False
    eu_cbam_exporter: bool = False
    fossil_fuel_involvement: bool = False
    project_summary: str
    climate_rationale: str
    technology_and_innovation: str
    esg_and_social_impact: str
    key_risks_and_mitigants: str


class FilledFormField(BaseModel):
    """Single auto-filled field output with provenance, confidence, and compliance feedback."""

    field_id: str
    label: str
    section: str
    value: Any
    status: FieldFillStatus
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning_mode: str  # KAG, RAG, HYBRID_KAG_RAG
    evidence_sources: List[str] = Field(default_factory=list)
    kag_reasoning_path: Optional[str] = None
    rag_citations: List[str] = Field(default_factory=list)
    compliance_notes: List[str] = Field(default_factory=list)


class EligibilityEvaluation(BaseModel):
    """Structured KAG/RAG eligibility decision before/during form filling."""

    eligible: bool
    fit_score: float = Field(..., ge=0.0, le=100.0)
    passed_checks: List[str]
    failed_checks: List[str]
    warnings: List[str]
    recommended_instrument: str
    kag_hops_executed: int = 0


class FilledApplicationPacket(BaseModel):
    """Full investor-specific auto-filled application form package."""

    submission_id: str
    generated_at_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    investor_id: str
    investor_name: str
    model_architecture: AIModelArchitecture
    form_template_id: FormTemplateType
    form_title: str
    project_id: str
    project_title: str
    pii_redacted_for_ai_context: bool = True
    tenant_isolation_verified: bool = True
    eligibility: EligibilityEvaluation
    completion_rate_percent: float
    average_confidence: float
    fields: List[FilledFormField]
    pre_submission_checklist: List[str]
    llm_backend_used: str = "deterministic-grounded-synthesizer-v1"


class InvestorModelManifest(BaseModel):
    """Metadata manifest stored in each per-investor isolated model directory."""

    investor_id: str
    investor_name: str
    short_name: str
    category: InvestorCategory
    model_architecture: AIModelArchitecture
    ai_model_rationale: str
    form_template_type: FormTemplateType
    tenant_namespace: str
    tenant_key_fingerprint: str
    created_at_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    source_record_sha256: str
    has_kag_graph: bool
    has_rag_corpus: bool
    kag_nodes_count: int = 0
    kag_edges_count: int = 0
    rag_chunks_count: int = 0
    artifact_hashes: Dict[str, str] = Field(default_factory=dict)
