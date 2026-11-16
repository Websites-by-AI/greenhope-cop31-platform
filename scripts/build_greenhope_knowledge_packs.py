"""Builds:
1. Enriched 66-entity COP31 Business Forum V1 + Extended Ecosystem Registry (with explicit Relationship Status:
   Investor Confirmed / Finance Participant / COP31 Supporter / Potential Strategic Partner).
2. Canonical GREENHOPE_MASTER single-source-of-truth profile (`data/greenhope_master.json`) with 4-Tier IP Security Classification.
3. First 10 Fully Verified Investor Knowledge Packs (`investors/<slug>/`) with all 13 structured files including
   `evidence/verified_claims.json` and `application_questions.json`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.schemas import (
    AIModelArchitecture,
    EcosystemBranch,
    FormTemplateType,
    InvestorCategory,
    InvestorRecord,
    RelationshipStatus,
)

# Priority metadata overrides for existing 44 COP31 entities so every record carries exact V1 Tier / Priority / Status
V1_METADATA_MAP: Dict[str, Dict[str, Any]] = {
    "inv_bbva_group": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier A — Approach Immediately",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "Very High",
        "knowledge_pack_slug": "bbva",
        "greenhope_fit_notes": "Highest-priority commercial bank at COP31; explicitly bridges innovation-to-investment for real-world cleantech & city pilots via Climate Finance Hub pavilion.",
    },
    "inv_garanti_bbva": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier A — Approach Immediately",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "Very High",
        "knowledge_pack_slug": "garanti_bbva",
        "greenhope_fit_notes": "Local Türkiye Global Banking Partner of COP31; TRY 3.5T sustainable finance target ideal for GreenHope Turkish city pilot -> measurable climate impact -> scale.",
    },
    "inv_aiib": {
        "ecosystem_branch": EcosystemBranch.DEVELOPMENT_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier A — Approach Immediately",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "Very High",
        "knowledge_pack_slug": "aiib",
        "greenhope_fit_notes": "IMMEDIATE NOV 16 ANTALYA EVENT: $1.6B Türkiye climate package + Nov 14 AIIB-GGGI project-preparation & investment-ready pipeline partnership directly matching GreenHope architecture.",
    },
    "inv_world_bank_ibrd": {
        "ecosystem_branch": EcosystemBranch.DEVELOPMENT_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier A — Approach Immediately",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "Very High",
        "knowledge_pack_slug": "world_bank",
        "greenhope_fit_notes": "Target via World Bank Group intermediaries, country climate programs, guarantees, or municipal resilience pilots rather than a raw grant ask.",
    },
    "inv_ifc": {
        "ecosystem_branch": EcosystemBranch.DEVELOPMENT_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier A — Approach Immediately",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "Very High",
        "greenhope_fit_notes": "Private-sector arm of World Bank Group ecosystem; best channel for commercializing GreenHope city/industrial MRV & resilience deployments.",
    },
    "inv_qnb_turkiye": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier A — Approach Immediately",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "High",
        "knowledge_pack_slug": "qnb",
        "greenhope_fit_notes": "COP31 Business Forum Finance WG member & $500M sustainable financing signer (incl. €75M Proparco); active green equipment leasing & SME climate lines.",
    },
    "inv_hsbc": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier A — Approach Immediately",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "High",
        "knowledge_pack_slug": "hsbc",
        "greenhope_fit_notes": "HSBC / HSBC Türkiye P1 banking & climate asset management partner in COP31 Business Forum Working Group; transition finance & supply-chain MRV alignment.",
    },
    "inv_akbank": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier B — Core Follow-Up",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "High",
        "knowledge_pack_slug": "akbank",
        "greenhope_fit_notes": "TRY 2.5T sustainable finance target + GEFF Türkiye & circular economy/waste programs directly matching GreenHope waste & municipal climate analytics.",
    },
    "inv_yapi_kredi": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
        "priority_tier": "Tier B — Core Follow-Up",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "High",
        "greenhope_fit_notes": "COP31 'Dönüşüme Tam Destek' twin green+digital program aligns well with GreenHope AI-powered environmental MRV & water/waste analytics.",
    },
    "inv_ziraat_bankasi": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
        "priority_tier": "Tier B — Core Follow-Up",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "High",
        "greenhope_fit_notes": "Strong for agricultural/OIZ green SME pilots; less direct fit for early-stage urban climate-AI software than BBVA unless paired with an OIZ or agri municipality.",
    },
    "inv_halkbank": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
        "priority_tier": "Tier B — Core Follow-Up",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "Medium-High",
        "greenhope_fit_notes": "TRY 100B COP31 SME Sustainability package (31 credit products, KGF-backed); suitable once GreenHope pilot partners with Turkish SMEs or municipalities.",
    },
    "inv_ebrd": {
        "ecosystem_branch": EcosystemBranch.DEVELOPMENT_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier C — Ecosystem / Strategic",
        "ai_rag_priority": "P1",
        "greenhope_relevance": "Very High",
        "greenhope_fit_notes": "EBRD Green Cities & GET 2026-30 Strategy directly finance urban resilience, waste, air quality, and digital MRV across Turkish municipalities.",
    },
    "inv_adb": {
        "ecosystem_branch": EcosystemBranch.DEVELOPMENT_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier C — Ecosystem / Strategic",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "High",
        "greenhope_fit_notes": "$3.1B Türkiye development portfolio + urban/disaster resilience focus; pathway via sovereign/municipal technical assistance or VakıfBank SME channel.",
    },
    "inv_isdb": {
        "ecosystem_branch": EcosystemBranch.DEVELOPMENT_BANKS,
        "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
        "priority_tier": "Tier C — Ecosystem / Strategic",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "High",
        "greenhope_fit_notes": "Shariah-compliant climate resilience & TIDIP partner; viable for OIC member-country urban adaptation and circular-waste pilots.",
    },
    "inv_gfanz_ccr": {
        "ecosystem_branch": EcosystemBranch.CLIMATE_FINANCE_NETWORKS,
        "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
        "priority_tier": "Tier C — Ecosystem / Strategic",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "High",
        "greenhope_fit_notes": "COP31 Catalytic Capital Repository maps 30+ catalytic funders & risk-mitigation vehicles for scaling GreenHope pilots in emerging markets.",
    },
    "inv_isbank": {
        "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
        "relationship_status": RelationshipStatus.COP31_SUPPORTER,
        "priority_tier": "Tier C — Ecosystem / Strategic",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "High",
        "greenhope_fit_notes": "Officially listed as COP31 Climate Supporter; verify specific green SME/blue-economy credit desk mandate before treating as direct GreenHope investor.",
    },
    "inv_tskb": {
        "ecosystem_branch": EcosystemBranch.DEVELOPMENT_BANKS,
        "relationship_status": RelationshipStatus.COP31_SUPPORTER,
        "priority_tier": "Tier C — Ecosystem / Strategic",
        "ai_rag_priority": "P2",
        "greenhope_relevance": "High",
        "greenhope_fit_notes": "COP31 Climate Supporter & Türkiye's sole IDFC member; strong MDB on-lending & green advisory partner for scaling GreenHope corporate/industrial deployments.",
    },
}


def get_additional_v1_and_ecosystem_entities() -> List[InvestorRecord]:
    """22 additional verified entities from the COP31 Business Forum Climate Finance & Investments WG + wider ecosystem."""
    raw = [
        # --- TIER A / P1 INVESTORS ---
        {
            "investor_id": "inv_meridiam",
            "name": "Meridiam",
            "short_name": "Meridiam",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "ecosystem_branch": EcosystemBranch.INFRASTRUCTURE_IMPACT_INVESTORS,
            "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
            "priority_tier": "Tier A — Approach Immediately",
            "ai_rag_priority": "P1",
            "greenhope_relevance": "Very High",
            "knowledge_pack_slug": "meridiam",
            "greenhope_fit_notes": "Global sustainable urban infrastructure impact investor (COP31 Business Forum Finance WG); strong synergy with GreenHope city resilience, smart waste, air quality & municipal PPP pilots.",
            "hq_country": "France",
            "geographic_focus": ["Global", "Europe", "Türkiye", "Africa", "North America", "Emerging Markets"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member focusing on bankable resilient urban infrastructure",
            "cop31_verified_2026_commitment": "Long-term sustainable infrastructure & urban climate resilience investment mandate (25-year impact fund model, active in Türkiye & global municipal PPPs)",
            "financing_instruments": ["Infrastructure Equity", "Municipal PPP Capital", "Urban Resilience Fund", "Blended Project Preparation"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 250_000_000,
            "target_sectors": ["Resilient Cities & Infrastructure", "Urban Mobility & Transport", "Zero Waste & Circular Economy", "Climate Adaptation & Resilience", "Renewable Energy"],
            "eligible_applicant_types": ["Municipality", "Project SPV", "Climate-Tech Startup", "Large Corporate"],
            "application_portal_url": "https://www.meridiam.com/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Measurable UN SDG & urban climate resilience impact metrics (MRV verified)",
                "Public-private partnership (PPP) or municipal concession scalability",
                "Long-term asset durability & Paris Alignment",
                "Strong environmental, social & community governance",
            ],
            "exclusion_rules": ["Coal or fossil-fuel infrastructure", "Short-term speculative non-impact ventures"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG checks municipal PPP & resilience infrastructure criteria while RAG tailors GreenHope city-pilot impact narratives to Meridiam's SDG impact framework.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_m_and_g",
            "name": "M&G (M&G Investments / Catalyst)",
            "short_name": "M&G",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "ecosystem_branch": EcosystemBranch.INFRASTRUCTURE_IMPACT_INVESTORS,
            "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
            "priority_tier": "Tier A — Approach Immediately",
            "ai_rag_priority": "P1",
            "greenhope_relevance": "High",
            "knowledge_pack_slug": "m_and_g",
            "greenhope_fit_notes": "Global asset manager & Catalyst private-assets climate impact investor (COP31 Business Forum WG); backs innovative climate-tech & measurable MRV impact businesses.",
            "hq_country": "United Kingdom",
            "geographic_focus": ["Global", "Europe", "United Kingdom", "Emerging Markets", "Türkiye"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member mobilizing institutional & private impact capital",
            "cop31_verified_2026_commitment": "Institutional climate transition & M&G Catalyst (£5B purpose-led private capital mandate) investing in scalable climate innovation & resilience",
            "financing_instruments": ["Private Growth Equity", "Impact Debt", "Catalyst Climate Innovation Capital", "Institutional Co-Investment"],
            "typical_ticket_min_usd": 3_000_000,
            "typical_ticket_max_usd": 150_000_000,
            "target_sectors": ["Climate-Tech Innovation", "Climate Adaptation & Resilience", "Circular Economy & Zero Waste", "Renewable Energy", "Resilient Cities & Infrastructure"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Growth-Stage Private Enterprise", "Project SPV", "Fund Manager"],
            "application_portal_url": "https://www.mandg.com/investments/institutional/en-gb/solutions/catalyst",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Clear commercial scalability & repeatable revenue model",
                "Verified measurable environmental/climate impact KPIs (IMP / IRIS+)",
                "Defensible technology or data moat (e.g., AI + MRV)",
                "Strong governance & institutional reporting readiness",
            ],
            "exclusion_rules": ["Thermal coal", "Unverified greenwashing claims"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG maps GreenHope's AI-driven MRV and scalable pilot economics to M&G Catalyst's purpose-led private assets investment thesis.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        # --- TIER B / P1 & P2 BANKS ---
        {
            "investor_id": "inv_deutsche_bank",
            "name": "Deutsche Bank",
            "short_name": "Deutsche Bank",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P1",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "COP31 Business Forum Climate Finance WG member; active in sustainable finance structuring, green bonds & European/EM transition capital.",
            "hq_country": "Germany",
            "geographic_focus": ["Global", "Europe", "Germany", "EMEA", "Türkiye", "Asia-Pacific", "Americas"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member",
            "cop31_verified_2026_commitment": "Sustainable finance & ESG investment banking mobilization (€500B+ cumulative sustainable finance framework) covering transition & green capital markets",
            "financing_instruments": ["Green Bond Underwriting", "Sustainability-Linked Loan (SLL)", "Transition Finance", "Blended Climate Fund Structuring"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 400_000_000,
            "target_sectors": ["Renewable Energy", "Industrial Decarbonization", "Resilient Cities & Infrastructure", "Climate-Tech Innovation", "Clean Transport"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Municipality"],
            "application_portal_url": "https://www.db.com/what-we-do/focus-topics/sustainability/",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "Deutsche Bank Sustainable Finance Framework & EU Taxonomy alignment",
                "ICMA GBP / LMA GLP or SLLP verification",
                "Second-Party Opinion (SPO) & audited credit profile",
                "Scope 1/2/3 GHG reporting",
            ],
            "exclusion_rules": ["Thermal coal mining/power expansion"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG aligns EU Taxonomy, green bond, and transition structuring narratives with Deutsche Bank's Sustainable Finance Framework.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_denizbank",
            "name": "DenizBank",
            "short_name": "DenizBank",
            "category": InvestorCategory.TURKISH_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.INVESTOR_CONFIRMED,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P1",
            "greenhope_relevance": "High",
            "knowledge_pack_slug": "denizbank",
            "greenhope_fit_notes": "COP31 Business Forum Climate Finance WG Turkish bank (Emirates NBD group); strong Antalya/Mediterranean municipal, agri, tourism & startup innovation ecosystem footprint.",
            "hq_country": "Türkiye (Emirates NBD Group)",
            "geographic_focus": ["Türkiye", "MENA"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member; local Turkish green finance & innovation banking leader",
            "cop31_verified_2026_commitment": "Sustainable agriculture, renewable energy, green SME & municipal climate-resilience financing across Türkiye (backed by Emirates NBD & DFI green credit lines)",
            "financing_instruments": ["Green SME Loan", "Sustainable Agriculture & Water Credit", "Renewable Energy Loan", "DFI On-Lending Line", "Startup/Tech Banking (Deniz Ventures)"],
            "typical_ticket_min_usd": 50_000,
            "typical_ticket_max_usd": 75_000_000,
            "target_sectors": ["Sustainable Agriculture & Water", "Renewable Energy", "SME Green Transition", "Climate-Tech Innovation", "Sustainable Tourism", "Zero Waste & Circular Economy"],
            "eligible_applicant_types": ["SME", "Climate-Tech Startup", "Large Corporate", "Municipality", "Project SPV"],
            "application_portal_url": "https://www.denizbank.com/en/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish company registration (VKN) & credit profile",
                "Eligible green transition, water/agri, or climate-tech use of proceeds",
                "Environmental compliance (ÇED/EIA) & measurable resource/CO2 savings",
                "Collateral / KGF guarantee or Deniz Ventures equity review",
            ],
            "exclusion_rules": ["Thermal coal expansion", "Non-compliant environmental activities"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG retrieves DenizBank's green SME, agri-tech, municipal, and Deniz Ventures climate-tech pathways for tailored Turkish applications.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_emirates_nbd",
            "name": "Emirates NBD",
            "short_name": "Emirates NBD",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "Parent of DenizBank & COP31 Business Forum WG bank; $30B sustainable finance target across MENA & Türkiye with green bonds and climate-tech innovation corridor.",
            "hq_country": "United Arab Emirates",
            "geographic_focus": ["MENA", "Türkiye", "EMEA", "Asia"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member",
            "cop31_verified_2026_commitment": "$30B sustainable finance target by 2030 covering green loans, sustainability-linked finance & MENA-Türkiye climate transition corridors",
            "financing_instruments": ["Green Loan", "Sustainability-Linked Loan (SLL)", "Green Bond / Green Sukuk", "Trade & Transition Finance"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Renewable Energy", "Resilient Cities & Infrastructure", "Water & Climate Adaptation", "Industrial Decarbonization", "Clean Transport"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Mid-Cap Enterprise"],
            "application_portal_url": "https://www.emiratesnbd.com/en/sustainability",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "Emirates NBD Sustainable Finance Framework alignment",
                "ICMA GBP / LMA GLP compliance & KPI reporting",
                "Credit underwriting & Second-Party Opinion for labeled issuances",
            ],
            "exclusion_rules": ["Unabated coal projects"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG grounds MENA/Türkiye green loan and green sukuk structures in Emirates NBD's Sustainable Finance Framework.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_lloyds",
            "name": "Lloyds Banking Group",
            "short_name": "Lloyds",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "COP31 Business Forum Finance WG member; active in UK/European green buildings, municipal net-zero & clean growth financing.",
            "hq_country": "United Kingdom",
            "geographic_focus": ["United Kingdom", "Europe", "EMEA"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member",
            "cop31_verified_2026_commitment": "Clean Growth Finance Initiative & £30B+ sustainable financing commitment for corporate/SME transition & green built environment",
            "financing_instruments": ["Green Loan", "Sustainability-Linked Loan", "Clean Growth Finance Facility", "Green Bond Underwriting"],
            "typical_ticket_min_usd": 2_000_000,
            "typical_ticket_max_usd": 250_000_000,
            "target_sectors": ["Green Buildings", "Renewable Energy", "Clean Transport", "Circular Economy & Zero Waste", "SME Green Transition"],
            "eligible_applicant_types": ["Large Corporate", "SME", "Mid-Cap Enterprise", "Project SPV"],
            "application_portal_url": "https://www.lloydsbankinggroup.com/who-we-are/responsible-business/environment.html",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "UK/European operating Nexus & Clean Growth Finance criteria",
                "LMA GLP / SLLP alignment & verified carbon reduction KPIs",
                "Commercial creditworthiness & ESG screening",
            ],
            "exclusion_rules": ["New thermal coal projects", "New oil & gas fields"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG aligns borrower applications with Lloyds' Clean Growth Finance Initiative eligibility schedules.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_standard_bank",
            "name": "Standard Bank Group",
            "short_name": "Standard Bank",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "Africa's largest bank by assets in COP31 Business Forum WG; ideal channel for scaling GreenHope climate resilience & air/waste pilots across African cities.",
            "hq_country": "South Africa",
            "geographic_focus": ["Africa", "Sub-Saharan Africa", "South Africa", "Kenya"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member",
            "cop31_verified_2026_commitment": "ZAR 250–300B+ sustainable finance mobilization across African renewable energy, climate resilience & urban infrastructure",
            "financing_instruments": ["Green Loan", "Sustainability-Linked Loan", "Renewable Project Finance", "Blended Adaptation Finance"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 250_000_000,
            "target_sectors": ["Renewable Energy", "Electrification & Grid", "Climate Adaptation & Resilience", "Sustainable Agriculture & Water", "Resilient Cities & Infrastructure"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Municipality", "Financial Intermediary"],
            "application_portal_url": "https://www.standardbank.com/sbg/standard-bank-group/about-us/sustainability",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "African operating presence & Equator Principles screening",
                "Standard Bank Sustainable Finance Framework alignment",
                "Bankable cash flows or DFI partial risk guarantee",
            ],
            "exclusion_rules": ["New coal-fired power plants"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG tailors African urban resilience and renewable transition applications to Standard Bank's Sustainable Finance Framework.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_cba_australia",
            "name": "Commonwealth Bank of Australia (CommBank)",
            "short_name": "CommBank (CBA)",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "Medium-High",
            "greenhope_fit_notes": "Key Australian bank in COP31 Business Forum WG (Australia co-presiding COP31 negotiations); strong sustainability-linked & clean tech financing for Asia-Pacific expansion.",
            "hq_country": "Australia",
            "geographic_focus": ["Australia", "Asia-Pacific", "Global"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member (Australian COP31 co-presidency financial delegation)",
            "cop31_verified_2026_commitment": "AUD 70B cumulative sustainability funding target by 2030 across clean energy, low-carbon transport & resilient infrastructure",
            "financing_instruments": ["Green Loan", "Sustainability-Linked Loan", "Green Bond Underwriting", "Clean Tech Corporate Debt"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Renewable Energy", "Energy Storage", "Clean Transport", "Green Buildings", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Mid-Cap Enterprise"],
            "application_portal_url": "https://www.commbank.com.au/about-us/opportunity-initiatives/sustainability.html",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "Asia-Pacific / Australian commercial nexus",
                "APLMA GLP/SLLP compliance & climate KPIs",
                "Audited corporate credit assessment",
            ],
            "exclusion_rules": ["Thermal coal mining/generation"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG aligns clean-tech and transition proposals with CommBank's Sustainability Funding Target criteria.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_anz",
            "name": "ANZ (Australia and New Zealand Banking Group)",
            "short_name": "ANZ",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "Medium-High",
            "greenhope_fit_notes": "COP31 Business Forum WG Australian bank; AUD 100B social & environmental sustainability target with focus on APAC energy transition & resilience.",
            "hq_country": "Australia",
            "geographic_focus": ["Australia", "Asia-Pacific", "Global"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member",
            "cop31_verified_2026_commitment": "AUD 100B environmental & social sustainability target by 2030 across APAC renewable energy, green buildings & climate adaptation",
            "financing_instruments": ["Green Loan", "Sustainability-Linked Loan", "Green Bond Structuring", "Transition Finance"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Renewable Energy", "Climate Adaptation & Resilience", "Green Buildings", "Industrial Decarbonization"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary"],
            "application_portal_url": "https://www.anz.com.au/about-us/esg/environmental-sustainability/",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "ANZ Social & Environmental Sustainability Target eligibility",
                "APLMA GLP/SLLP alignment & verified GHG KPIs",
                "Credit underwriting & SPO for labeled facilities",
            ],
            "exclusion_rules": ["New thermal coal projects"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG retrieves ANZ's APAC transition & sustainability framework guidance for institutional loan structuring.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_aib",
            "name": "AIB (Allied Irish Banks)",
            "short_name": "AIB",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "ecosystem_branch": EcosystemBranch.COMMERCIAL_BANKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier B — Core Follow-Up",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "Medium",
            "greenhope_fit_notes": "COP31 Business Forum Finance WG member; €30B Climate Action Fund focused primarily on Ireland/UK/EU renewable energy & green transition.",
            "hq_country": "Ireland",
            "geographic_focus": ["Europe", "EU", "United Kingdom"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member",
            "cop31_verified_2026_commitment": "€30B Climate Action Fund supporting European renewables, green buildings & transition finance",
            "financing_instruments": ["Green Loan", "Renewable Project Finance", "Green Bond"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 150_000_000,
            "target_sectors": ["Renewable Energy", "Green Buildings", "Energy Efficiency", "Clean Transport"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "SME"],
            "application_portal_url": "https://aib.ie/sustainability",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "EU / Ireland / UK project nexus",
                "EU Taxonomy & AIB Green Bond Framework alignment",
                "Credit underwriting & EIA compliance",
            ],
            "exclusion_rules": ["Fossil-fuel generation"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG aligns European renewable/green-building requests with AIB's €30B Climate Action Fund criteria.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        # --- TIER C / P2 ECOSYSTEM, NETWORKS, PUBLIC FACILITATORS & INSURERS ---
        {
            "investor_id": "inv_zurich_turkiye",
            "name": "Zurich Life & Pension Türkiye (Zurich Group)",
            "short_name": "Zurich Türkiye",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "ecosystem_branch": EcosystemBranch.INFRASTRUCTURE_IMPACT_INVESTORS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "Medium",
            "greenhope_fit_notes": "COP31 Business Forum WG insurance/institutional investor in Türkiye; potential partner for climate-risk parametric insurance & resilient city pilot de-risking.",
            "hq_country": "Türkiye (Switzerland Parent)",
            "geographic_focus": ["Türkiye", "Europe", "Global"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member (Insurance & Resilience Finance)",
            "cop31_verified_2026_commitment": "Climate resilience risk-transfer, parametric insurance & ESG pension fund impact investing in Türkiye",
            "financing_instruments": ["Climate Resilience Insurance", "ESG Institutional Allocation", "Impact Bond Allocation"],
            "typical_ticket_min_usd": 1_000_000,
            "typical_ticket_max_usd": 50_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Resilient Cities & Infrastructure", "Sustainable Agriculture & Water"],
            "eligible_applicant_types": ["Municipality", "Large Corporate", "Project SPV", "Fund Manager"],
            "application_portal_url": "https://www.zurich.com/sustainability",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Quantifiable climate risk reduction or resilience impact",
                "Institutional-grade governance & impact reporting",
                "Alignment with Zurich Net-Zero & Climate Resilience priorities",
            ],
            "exclusion_rules": ["Thermal coal underwriting/investment"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG maps urban/agricultural climate resilience metrics to Zurich's risk-transfer and ESG investment criteria.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_invest_tr",
            "name": "Investment and Finance Office of the Presidency of Türkiye (Invest in Türkiye)",
            "short_name": "Invest in Türkiye",
            "category": InvestorCategory.CLIMATE_FINANCE_NETWORK,
            "ecosystem_branch": EcosystemBranch.CLIMATE_FINANCE_NETWORKS,
            "relationship_status": RelationshipStatus.POTENTIAL_STRATEGIC_PARTNER,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "Very High",
            "greenhope_fit_notes": "Very High strategic leverage: public investment facilitation hub at COP31 Antalya connecting GreenHope directly to sovereign funds, MDBs, Turkish ministries & municipal pilots.",
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye", "Global"],
            "cop31_antalya_role": "Official COP31 Antalya host investment agency & Business Forum Climate Finance WG co-convener",
            "cop31_verified_2026_commitment": "Facilitating FDI, green industrial zones, clean-tech incentives & MDB/private investor matchmaking across Türkiye's 2053 Net Zero agenda",
            "financing_instruments": ["Investment Matchmaking", "Government Incentive Facilitation", "Public-Private Pilot Introduction"],
            "typical_ticket_min_usd": 0,
            "typical_ticket_max_usd": 500_000_000,
            "target_sectors": ["Climate-Tech Innovation", "Industrial Decarbonization", "Renewable Energy", "Resilient Cities & Infrastructure", "Zero Waste & Circular Economy"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Large Corporate", "Project SPV", "Municipality", "Fund Manager"],
            "application_portal_url": "https://www.invest.gov.tr/en/pages/home-page.aspx",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Clear investment & job-creation roadmap in Türkiye",
                "Alignment with Türkiye Green Deal Action Plan & 2053 Net Zero",
                "Verified technology readiness & municipal/corporate pilot scope",
            ],
            "exclusion_rules": ["Non-compliant speculative schemes"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG structures strategic executive briefs for Turkish investment facilitation & incentive desk introductions.",
            "verification_source_url": "https://www.dailysabah.com/business/energy/climate-finance-investment-talks-to-feature-high-on-cop31-agenda/amp",
        },
        {
            "investor_id": "inv_gefi",
            "name": "Global Ethical Finance Initiative (GEFI)",
            "short_name": "GEFI",
            "category": InvestorCategory.CLIMATE_FINANCE_NETWORK,
            "ecosystem_branch": EcosystemBranch.CLIMATE_FINANCE_NETWORKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "COP31 Business Forum Finance WG network bridging Islamic/ethical finance, green sukuk & SDG impact investors with climate innovation pipelines.",
            "hq_country": "United Kingdom",
            "geographic_focus": ["Global", "Türkiye", "MENA", "Europe", "Asia", "Africa"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member (Path to COP31 Ethical & Islamic Climate Finance)",
            "cop31_verified_2026_commitment": "Mobilizing ethical & Shariah-aligned institutional investors toward SDG & Paris-aligned climate projects via Path to COP31 platform",
            "financing_instruments": ["Ethical Investor Syndicate Intro", "Green Sukuk Structuring Network", "Impact Dealroom Access"],
            "typical_ticket_min_usd": 500_000,
            "typical_ticket_max_usd": 100_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Renewable Energy", "Zero Waste & Circular Economy", "Sustainable Agriculture & Water", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Project SPV", "SME", "Fund Manager", "Large Corporate"],
            "application_portal_url": "https://www.globalethicalfinance.org/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Strong UN SDG alignment & ethical/transparent governance",
                "Verified measurable environmental & social impact",
                "Clear investable pilot or blended-finance structure",
            ],
            "exclusion_rules": ["Non-ethical or fossil-fuel-intensive activities"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG tailors ethical & SDG-aligned dealroom pitches for GEFI's COP31 investor coalition.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_fast_infra",
            "name": "FAST-Infra Group",
            "short_name": "FAST-Infra",
            "category": InvestorCategory.CLIMATE_FINANCE_NETWORK,
            "ecosystem_branch": EcosystemBranch.CLIMATE_FINANCE_NETWORKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "COP31 Business Forum WG sustainable infrastructure label & platform; GreenHope's MRV/AI verification layer maps directly to FAST-Infra Sustainable Infrastructure Label (SI Label) data needs!",
            "hq_country": "France / Switzerland (Global Coalition)",
            "geographic_focus": ["Global", "Emerging Markets", "Türkiye", "Africa", "Asia", "Latin America"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member scaling labeled sustainable infrastructure",
            "cop31_verified_2026_commitment": "Deploying the FAST-Infra Sustainable Infrastructure Label & Technology-Enabled Data Platform to turn resilient urban/green infrastructure into a liquid asset class",
            "financing_instruments": ["Sustainable Infrastructure Labeling", "Institutional Deal Flow Acceleration", "Blended Infrastructure Facility Intro"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Resilient Cities & Infrastructure", "Climate Adaptation & Resilience", "Renewable Energy", "Water & Wastewater Management", "Zero Waste & Circular Economy"],
            "eligible_applicant_types": ["Municipality", "Project SPV", "Climate-Tech Startup", "Large Corporate", "Financial Intermediary"],
            "application_portal_url": "https://www.fastinfragroup.org/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Alignment with FAST-Infra 14 sustainability criteria (Environmental, Social, Governance, Resilience)",
                "Verifiable digital MRV performance data",
                "Scalable emerging-market infrastructure pipeline",
            ],
            "exclusion_rules": ["Unlabeled fossil-fuel infrastructure"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG maps FAST-Infra's 14 label criteria while RAG shows how GreenHope's MRV engine enables infrastructure bankability.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_iiab",
            "name": "Impact Investing Advisory Board (EYDK / Türkiye Impact Network)",
            "short_name": "Impact Investing Board",
            "category": InvestorCategory.CLIMATE_FINANCE_NETWORK,
            "ecosystem_branch": EcosystemBranch.CLIMATE_FINANCE_NETWORKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "COP31 Business Forum WG impact-investing hub connecting Turkish/global impact VCs, family offices & foundations with verified impact startups like GreenHope.",
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye", "EMEA", "Global"],
            "cop31_antalya_role": "COP31 Business Forum Climate Finance & Investments Working Group member mobilizing domestic & global impact capital",
            "cop31_verified_2026_commitment": "Growing Türkiye's impact investing ecosystem across climate resilience, circular cities, social inclusion & verified impact measurement",
            "financing_instruments": ["Impact Investor Matchmaking", "Catalytic Impact Fund Access", "Venture Philanthropy Intros"],
            "typical_ticket_min_usd": 100_000,
            "typical_ticket_max_usd": 25_000_000,
            "target_sectors": ["Climate-Tech Innovation", "Climate Adaptation & Resilience", "Zero Waste & Circular Economy", "Resilient Cities & Infrastructure", "Sustainable Agriculture & Water"],
            "eligible_applicant_types": ["Climate-Tech Startup", "SME", "Accredited Entity/NGO", "Fund Manager"],
            "application_portal_url": "https://eydk.org/en/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Intentional, measurable social & environmental impact (IMP / IRIS+)",
                "Clear theory of change & verified pilot metrics",
                "Scalable business model in Türkiye/EMEA",
            ],
            "exclusion_rules": ["Purely philanthropic non-scalable projects without impact measurement"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG crafts concise IMP/IRIS+ impact briefs tailored to Türkiye's impact investor syndicate.",
            "verification_source_url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
        },
        {
            "investor_id": "inv_gfif",
            "name": "GFIF (Global Finance & Investment Forum at COP31)",
            "short_name": "GFIF Dealroom",
            "category": InvestorCategory.CLIMATE_FINANCE_NETWORK,
            "ecosystem_branch": EcosystemBranch.CLIMATE_FINANCE_NETWORKS,
            "relationship_status": RelationshipStatus.FINANCE_PARTICIPANT,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P2",
            "greenhope_relevance": "High",
            "greenhope_fit_notes": "COP31 capital-provider dealroom uniting lenders, guarantors, DFIs & institutional investors around structured climate finance deals.",
            "hq_country": "Global (COP31 Antalya Dealroom)",
            "geographic_focus": ["Global", "Emerging Markets", "Türkiye", "Africa", "Asia"],
            "cop31_antalya_role": "Convening lenders, guarantors, DFIs & capital providers in a dedicated COP31 Capital-Provider Dealroom",
            "cop31_verified_2026_commitment": "Structured climate dealroom connecting project developers, guarantors & DFIs to close bankability gaps at COP31 Antalya",
            "financing_instruments": ["Capital-Provider Dealroom", "Guarantee & Blended Structuring", "Co-Investment Syndication"],
            "typical_ticket_min_usd": 1_000_000,
            "typical_ticket_max_usd": 200_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Renewable Energy", "Resilient Cities & Infrastructure", "Industrial Decarbonization", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Project SPV", "Climate-Tech Startup", "Large Corporate", "Municipality", "Fund Manager"],
            "application_portal_url": "https://www.gfif.fund/cop31",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Bankable dealroom teaser with clear capital stack & guarantee needs",
                "Verified climate impact & MRV methodology",
                "Defined pilot or commercial deployment site",
            ],
            "exclusion_rules": ["Unstructured concept ideas lacking financial model"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG validates blended-finance capital stack & guarantor fit while RAG prepares crisp dealroom pitch sheets.",
            "verification_source_url": "https://www.gfif.fund/cop31",
        },
        {
            "investor_id": "inv_gggi",
            "name": "Global Green Growth Institute (GGGI)",
            "short_name": "GGGI",
            "category": InvestorCategory.CLIMATE_FINANCE_NETWORK,
            "ecosystem_branch": EcosystemBranch.CLIMATE_FINANCE_NETWORKS,
            "relationship_status": RelationshipStatus.POTENTIAL_STRATEGIC_PARTNER,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P1",
            "greenhope_relevance": "Very High",
            "greenhope_fit_notes": "Signed cooperation agreement with AIIB on Nov 14, 2026 at COP31 on project preparation, investment-ready pipelines, co-financing & technical assistance—key bridge for GreenHope into AIIB!",
            "hq_country": "South Korea (Intergovernmental)",
            "geographic_focus": ["Global", "Emerging Markets", "Developing Countries", "Türkiye", "Asia", "Africa", "Latin America"],
            "cop31_antalya_role": "Signed Nov 14, 2026 COP31 Antalya cooperation agreement with AIIB on climate-resilient infrastructure project preparation & green pipelines",
            "cop31_verified_2026_commitment": "Joint AIIB–GGGI project preparation, technical assistance & investment-ready climate-resilient infrastructure pipeline mobilization",
            "financing_instruments": ["Project Preparation Technical Assistance", "Green City Advisory", "MDB Pipeline Origination (AIIB/GCF)"],
            "typical_ticket_min_usd": 250_000,
            "typical_ticket_max_usd": 50_000_000,
            "target_sectors": ["Resilient Cities & Infrastructure", "Climate Adaptation & Resilience", "Zero Waste & Circular Economy", "Air Quality & Green Growth", "Renewable Energy"],
            "eligible_applicant_types": ["Sovereign/Government", "Municipality", "Climate-Tech Startup", "Project SPV"],
            "application_portal_url": "https://gggi.org/",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "Host-country / municipal green-growth policy alignment",
                "Clear path from technical assistance/pilot to AIIB or GCF bankable scale",
                "Measurable GHG, air quality, waste, or resilience KPIs",
            ],
            "exclusion_rules": ["Fossil-fuel expansion"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG maps the AIIB–GGGI joint project-preparation pathway while RAG aligns GreenHope city pilots with GGGI technical assistance criteria.",
            "verification_source_url": "https://www.aiib.org/en/news-events/news/2026/aiib-and-gggi-deepen-cooperation-climate-resilient-infrastructure-green-development.html",
        },
        # --- STRATEGIC / CORPORATE CAPITAL (Explicitly tagged COP31 SUPPORTER / STRATEGIC PARTNER — NOT falsely labeled Investor Confirmed!) ---
        {
            "investor_id": "inv_siemens",
            "name": "Siemens (Siemens Energy / Smart Infrastructure)",
            "short_name": "Siemens",
            "category": InvestorCategory.STRATEGIC_CORPORATE_PARTNER,
            "ecosystem_branch": EcosystemBranch.STRATEGIC_CORPORATE_CAPITAL,
            "relationship_status": RelationshipStatus.COP31_SUPPORTER,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P3",
            "greenhope_relevance": "Strategic Partner",
            "greenhope_fit_notes": "IMPORTANT DISTINCTION: Official COP31 Climate Supporter—NOT a confirmed direct startup funder. Approach for smart-city IoT/grid pilot technology partnership or corporate venture referral (Next47).",
            "hq_country": "Germany",
            "geographic_focus": ["Global", "Europe", "Türkiye"],
            "cop31_antalya_role": "Official COP31 Climate Supporter (Smart Infrastructure, Electrification & Industrial Decarbonization technology showcase)",
            "cop31_verified_2026_commitment": "COP31 Climate Supporter status; smart-city, grid digitalization & decarbonization technology partnerships (verify funding vs. vendor role)",
            "financing_instruments": ["Strategic Technology Pilot Partnership", "Corporate Venture Referral (Next47)", "Equipment Vendor Finance (SFS)"],
            "typical_ticket_min_usd": 0,
            "typical_ticket_max_usd": 50_000_000,
            "target_sectors": ["Resilient Cities & Infrastructure", "Electrification & Grid", "Industrial Decarbonization", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Large Corporate", "Municipality", "Climate-Tech Startup", "Project SPV"],
            "application_portal_url": "https://cop31.tr/partners/climate-supporters",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Verified distinction: do NOT assume direct grant/equity funding from COP31 Supporter badge",
                "Clear technical integration value with Siemens Smart Infrastructure / Xcelerator",
                "Protected IP boundaries (Level 1 PUBLIC pitch only prior to NDA)",
            ],
            "exclusion_rules": ["Unverified assumption of direct funding without formal CVC/SFS mandate"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG generates IP-safe corporate pilot partnership teasers while explicitly flagging COP31 Supporter (non-confirmed investor) status.",
            "verification_source_url": "https://cop31.tr/partners/climate-supporters",
        },
        {
            "investor_id": "inv_ge_vernova",
            "name": "GE Vernova",
            "short_name": "GE Vernova",
            "category": InvestorCategory.STRATEGIC_CORPORATE_PARTNER,
            "ecosystem_branch": EcosystemBranch.STRATEGIC_CORPORATE_CAPITAL,
            "relationship_status": RelationshipStatus.COP31_SUPPORTER,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P3",
            "greenhope_relevance": "Strategic Partner",
            "greenhope_fit_notes": "Official COP31 Climate Supporter—approach as electrification/grid corporate technology partner or CVC referral, NOT as a confirmed direct funder.",
            "hq_country": "United States",
            "geographic_focus": ["Global", "Türkiye", "Europe", "Americas"],
            "cop31_antalya_role": "Official COP31 Climate Supporter showcasing grid modernization, wind & electrification technologies",
            "cop31_verified_2026_commitment": "COP31 Climate Supporter & clean-power/grid technology deployment partner",
            "financing_instruments": ["Strategic Corporate Partnership", "Corporate Venture / Co-Development"],
            "typical_ticket_min_usd": 0,
            "typical_ticket_max_usd": 50_000_000,
            "target_sectors": ["Electrification & Grid", "Renewable Energy", "Energy Storage", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Climate-Tech Startup"],
            "application_portal_url": "https://cop31.tr/partners/climate-supporters",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Treat as Strategic Corporate Partner / COP31 Supporter (not confirmed investor)",
                "Share Level 1 PUBLIC overview only prior to mutual NDA",
            ],
            "exclusion_rules": ["Misrepresenting COP31 Supporter status as open grant funding"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG drafts grid/electrification technical collaboration briefs while enforcing Supporter-vs-Investor governance.",
            "verification_source_url": "https://cop31.tr/partners/climate-supporters",
        },
        {
            "investor_id": "inv_cisco",
            "name": "Cisco",
            "short_name": "Cisco",
            "category": InvestorCategory.STRATEGIC_CORPORATE_PARTNER,
            "ecosystem_branch": EcosystemBranch.STRATEGIC_CORPORATE_CAPITAL,
            "relationship_status": RelationshipStatus.COP31_SUPPORTER,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P3",
            "greenhope_relevance": "Strategic Partner",
            "greenhope_fit_notes": "Official COP31 Climate Supporter—potential smart-city networking / Cisco Foundation climate-grant referral partner, NOT automatically a direct equity funder.",
            "hq_country": "United States",
            "geographic_focus": ["Global", "Türkiye", "Europe"],
            "cop31_antalya_role": "Official COP31 Climate Supporter (Digital Sustainability & Connected Smart Cities)",
            "cop31_verified_2026_commitment": "COP31 Climate Supporter; Cisco Foundation climate regeneration grants & smart-city IoT infrastructure collaboration",
            "financing_instruments": ["Strategic Tech Partnership", "Cisco Foundation Climate Grant Referral", "Cisco Investments CVC Referral"],
            "typical_ticket_min_usd": 0,
            "typical_ticket_max_usd": 10_000_000,
            "target_sectors": ["Resilient Cities & Infrastructure", "Climate-Tech Innovation", "Air Quality & IoT", "Circular Economy & Zero Waste"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Municipality", "Accredited Entity/NGO"],
            "application_portal_url": "https://cop31.tr/partners/climate-supporters",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Distinguish COP31 Climate Supporter role from separate Cisco Foundation / CVC applications",
                "Protect Level 3/4 proprietary AI architecture before NDA",
            ],
            "exclusion_rules": ["Assuming COP31 Supporter badge equals open investor commitment"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG drafts smart-city IoT collaboration & Cisco Foundation alignment briefs cleanly.",
            "verification_source_url": "https://cop31.tr/partners/climate-supporters",
        },
        {
            "investor_id": "inv_sap",
            "name": "SAP",
            "short_name": "SAP",
            "category": InvestorCategory.STRATEGIC_CORPORATE_PARTNER,
            "ecosystem_branch": EcosystemBranch.STRATEGIC_CORPORATE_CAPITAL,
            "relationship_status": RelationshipStatus.POTENTIAL_STRATEGIC_PARTNER,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P3",
            "greenhope_relevance": "Strategic Partner",
            "greenhope_fit_notes": "Strategic enterprise ESG/carbon-accounting software ecosystem partner (SAP Sustainability Control Tower / Green Ledger); approach for MRV integration & corporate co-sell.",
            "hq_country": "Germany",
            "geographic_focus": ["Global", "Europe", "Türkiye"],
            "cop31_antalya_role": "Enterprise sustainability software & carbon accounting ecosystem participant",
            "cop31_verified_2026_commitment": "Corporate carbon ledger, ESG reporting & supply-chain MRV ecosystem partnerships",
            "financing_instruments": ["Enterprise Co-Sell / Ecosystem Partnership", "SAP.iO Venture Referral"],
            "typical_ticket_min_usd": 0,
            "typical_ticket_max_usd": 10_000_000,
            "target_sectors": ["Climate-Tech Innovation", "Industrial Decarbonization", "Circular Economy & Zero Waste", "Carbon Markets & Article 6"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Large Corporate"],
            "application_portal_url": "https://www.sap.com/sustainability.html",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "API / Green Ledger MRV interoperability value proposition",
                "IP-safe Level 1 PUBLIC sharing only",
            ],
            "exclusion_rules": ["Assuming direct grant funding from enterprise software partner"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG frames GreenHope MRV integration opportunities for SAP sustainability ecosystems.",
            "verification_source_url": "https://www.sap.com/sustainability.html",
        },
        {
            "investor_id": "inv_ikea",
            "name": "IKEA (Ingka Group / Ingka Investments)",
            "short_name": "IKEA",
            "category": InvestorCategory.STRATEGIC_CORPORATE_PARTNER,
            "ecosystem_branch": EcosystemBranch.STRATEGIC_CORPORATE_CAPITAL,
            "relationship_status": RelationshipStatus.COP31_SUPPORTER,
            "priority_tier": "Tier C — Ecosystem / Strategic",
            "ai_rag_priority": "P3",
            "greenhope_relevance": "Strategic Partner",
            "greenhope_fit_notes": "Official COP31 Climate Supporter—distinct from Ingka Investments (which separately invests in circular economy & renewables). Never conflate Supporter badge with open funding.",
            "hq_country": "Netherlands / Sweden",
            "geographic_focus": ["Global", "Europe", "Türkiye"],
            "cop31_antalya_role": "Official COP31 Climate Supporter promoting circular economy, zero waste & renewable energy",
            "cop31_verified_2026_commitment": "COP31 Climate Supporter; separate Ingka Investments circular-economy & clean-energy corporate investment arm",
            "financing_instruments": ["Strategic Circular Pilot Partner", "Ingka Investments Referral (Separate Mandate)"],
            "typical_ticket_min_usd": 0,
            "typical_ticket_max_usd": 50_000_000,
            "target_sectors": ["Zero Waste & Circular Economy", "Renewable Energy", "Sustainable Supply Chains"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Large Corporate", "SME"],
            "application_portal_url": "https://cop31.tr/partners/climate-supporters",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Separate COP31 Supporter participation from formal Ingka Investments mandate",
                "Demonstrate measurable circular-waste or retail decarbonization impact",
            ],
            "exclusion_rules": ["Treating COP31 Supporter sponsorship as confirmed funding"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG frames circular-economy pilot proposals cleanly while preserving Supporter vs. Investor boundaries.",
            "verification_source_url": "https://cop31.tr/partners/climate-supporters",
        },
    ]
    return [InvestorRecord.model_validate(r) for r in raw]


def enrich_investor_record(inv: InvestorRecord) -> InvestorRecord:
    """Apply V1 priority/status/branch metadata cleanly to any base investor record."""
    data = inv.model_dump()
    if inv.investor_id in V1_METADATA_MAP:
        data.update(V1_METADATA_MAP[inv.investor_id])
    else:
        # Clean defaults by category so every single one of the 66 records has crisp metadata
        cat = inv.category
        if cat in (InvestorCategory.MDB, InvestorCategory.BILATERAL_DFI, InvestorCategory.NATIONAL_DEV_BANK):
            data["ecosystem_branch"] = EcosystemBranch.DEVELOPMENT_BANKS
            data["relationship_status"] = RelationshipStatus.INVESTOR_CONFIRMED
            data["priority_tier"] = "Tier C — Ecosystem / Strategic"
            data["ai_rag_priority"] = "P2"
            data["greenhope_relevance"] = "High"
            data["greenhope_fit_notes"] = f"Development bank channel ({inv.short_name}); match via project preparation, municipal/sovereign pilots, or DFI blended co-financing."
        elif cat == InvestorCategory.CLIMATE_FUND:
            data["ecosystem_branch"] = EcosystemBranch.MULTILATERAL_CLIMATE_FUNDS
            data["relationship_status"] = RelationshipStatus.INVESTOR_CONFIRMED
            data["priority_tier"] = "Tier C — Ecosystem / Strategic"
            data["ai_rag_priority"] = "P2"
            data["greenhope_relevance"] = "High"
            data["greenhope_fit_notes"] = f"UNFCCC/Multilateral Climate Fund ({inv.short_name}); channel GreenHope city adaptation/mitigation pilot via an Accredited Entity or NDA."
        elif cat in (InvestorCategory.TURKISH_COMMERCIAL_BANK, InvestorCategory.TURKISH_STATE_BANK, InvestorCategory.GLOBAL_COMMERCIAL_BANK):
            data["ecosystem_branch"] = EcosystemBranch.COMMERCIAL_BANKS
            data["relationship_status"] = RelationshipStatus.FINANCE_PARTICIPANT
            data["priority_tier"] = "Tier C — Ecosystem / Strategic"
            data["ai_rag_priority"] = "P2"
            data["greenhope_relevance"] = "Medium-High"
            data["greenhope_fit_notes"] = f"COP31 banking participant ({inv.short_name}); verify active green transition or SME credit desk fit for GreenHope pilot scaling."
        elif cat == InvestorCategory.INSTITUTIONAL_CATALYTIC_PE:
            data["ecosystem_branch"] = EcosystemBranch.INFRASTRUCTURE_IMPACT_INVESTORS
            data["relationship_status"] = RelationshipStatus.INVESTOR_CONFIRMED
            data["priority_tier"] = "Tier C — Ecosystem / Strategic"
            data["ai_rag_priority"] = "P2"
            data["greenhope_relevance"] = "High"
            data["greenhope_fit_notes"] = f"Catalytic/institutional climate investor ({inv.short_name}); target for GreenHope pilot de-risking or growth equity."
    return InvestorRecord.model_validate(data)


def write_greenhope_master_profile(path: Path) -> dict:
    """Create the canonical GREENHOPE_MASTER single-source-of-truth profile with 4-Tier IP Security Classification."""
    master = {
        "schema_version": "1.0.0",
        "project_code": "GREENHOPE_MASTER",
        "last_updated_utc": "2026-11-15T12:00:00Z",
        "security_policy": {
            "LEVEL_1_PUBLIC": {
                "label": "Level 1 — PUBLIC",
                "auto_submit_allowed": True,
                "ai_matching_allowed": True,
                "description": "Safe for investor application forms: mission, public demo, high-level architecture, public environmental problem, public team.",
            },
            "LEVEL_2_INTERNAL": {
                "label": "Level 2 — INTERNAL",
                "auto_submit_allowed": False,
                "requires_human_approval": True,
                "ai_matching_allowed": True,
                "description": "Used for investor matching & draft proposals; requires explicit human confirmation before submission (financing scenarios, pilot budget, business model).",
            },
            "LEVEL_3_CONFIDENTIAL": {
                "label": "Level 3 — CONFIDENTIAL",
                "auto_submit_allowed": False,
                "requires_human_approval": True,
                "ai_matching_allowed": False,
                "description": "Blocked from automatic form filling: unpublished technical architecture, proprietary algorithms, detailed data pipeline, unpublished research.",
            },
            "LEVEL_4_RESTRICTED": {
                "label": "Level 4 — RESTRICTED",
                "auto_submit_allowed": False,
                "requires_human_approval": False,
                "ai_matching_allowed": False,
                "description": "Strictly blocked from AI exposure and external forms: patentable inventions, API keys/credentials, private investor comms, personal PII, confidential contracts.",
            },
        },
        "canonical_fields": {
            "organization": {
                "section": "Organization",
                "classification": "LEVEL_1_PUBLIC",
                "value": "GreenHope Climate Intelligence Initiative",
                "source": "GreenHope Canonical Profile v1",
                "confidence": 0.99,
            },
            "founder_team": {
                "section": "Founder / Team",
                "classification": "LEVEL_1_PUBLIC",
                "value": "GreenHope Founding Team — Climate AI, Urban Environmental Analytics & Climate Finance Architecture (Antalya / Türkiye)",
                "source": "GreenHope Public Team Bio",
                "confidence": 0.96,
            },
            "problem": {
                "section": "Problem",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Cities in Türkiye and emerging markets face compounding urban air-quality degradation, municipal waste inefficiencies, and climate shocks, yet struggle to convert environmental data into bankable, MRV-verified climate projects eligible for MDB and bank financing.",
                "source": "GreenHope Mission Statement",
                "confidence": 0.98,
            },
            "solution": {
                "section": "Solution",
                "classification": "LEVEL_1_PUBLIC",
                "value": "GreenHope is an AI-enabled urban climate resilience and environmental intelligence platform linking city pilots (air quality, waste optimization, urban resilience) directly to verified MRV metrics and climate finance mobilization (GreenHope -> city pilot -> measurable climate impact -> financing -> scale).",
                "source": "GreenHope Public Architecture Summary",
                "confidence": 0.98,
            },
            "technology": {
                "section": "Technology",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Modular cloud + IoT environmental telemetry integration, geospatial urban analytics, automated MRV reporting dashboards, and KAG+RAG climate finance matching.",
                "source": "GreenHope Public Technical Overview",
                "confidence": 0.95,
            },
            "ai": {
                "section": "AI",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Applied AI combining environmental forecasting, anomaly detection for urban air/waste systems, and Knowledge-Augmented Generation (KAG) + RAG for transparent MRV and climate finance readiness.",
                "source": "GreenHope AI Overview (Public)",
                "confidence": 0.95,
            },
            "environmental_impact": {
                "section": "Environmental impact",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Measurable reductions in urban air-pollution exposure, landfill methane/waste leakage, and municipal energy waste via real-time operational intervention.",
                "source": "GreenHope Impact Framework",
                "confidence": 0.94,
            },
            "climate_impact": {
                "section": "Climate impact",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Dual mitigation & adaptation impact: quantified tCO2e reductions (waste circularity & urban efficiency) alongside real-time urban heat/air-quality resilience for municipal populations.",
                "source": "GreenHope Climate Rationale",
                "confidence": 0.95,
            },
            "air_quality": {
                "section": "Air quality",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Hyper-local urban air-quality monitoring, PM2.5/NOx hotspot detection, and predictive mitigation guidance for cities and industrial zones.",
                "source": "GreenHope Air Quality Module",
                "confidence": 0.96,
            },
            "waste": {
                "section": "Waste",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Smart municipal waste analytics supporting COP31 Türkiye Zero Waste priorities: diversion tracking, methane reduction, and circular recovery verification.",
                "source": "GreenHope Zero Waste Module",
                "confidence": 0.96,
            },
            "cities": {
                "section": "Cities",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Designed for rapid deployment in Mediterranean and emerging-market municipalities (initial flagship pilot focus: Antalya & Turkish metropolitan cities, scalable across EMEA/Asia/Africa).",
                "source": "GreenHope City Pilot Strategy",
                "confidence": 0.96,
            },
            "target_users": {
                "section": "Target users",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Municipalities, metropolitan climate departments, organized industrial zones (OIZs), development banks/commercial lenders requiring verified MRV, and urban sustainability operators.",
                "source": "GreenHope Market Profile",
                "confidence": 0.95,
            },
            "pilot": {
                "section": "Pilot",
                "classification": "LEVEL_2_INTERNAL",
                "value": "12-month Flagship Municipal City Pilot (Antalya / Türkiye) demonstrating real-time air quality + waste MRV dashboards and generating investment-grade impact metrics for follow-on bank/MDB scale-up.",
                "source": "GreenHope Pilot Roadmap (Internal)",
                "confidence": 0.94,
            },
            "geography": {
                "section": "Geography",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Initial pilot: Antalya, Türkiye (COP31 host city); regional expansion across Türkiye, Europe/EMEA, and emerging markets.",
                "source": "GreenHope Geographic Scope",
                "confidence": 0.99,
            },
            "funding_requirement": {
                "section": "Funding requirement",
                "classification": "LEVEL_2_INTERNAL",
                "value": "USD 50,000 – USD 250,000 initial city pilot & technical preparation funding (scaling to USD 1M–5M blended/project finance alongside MDB/bank municipal partners)",
                "source": "GreenHope Financial Model (Pilot Tranche)",
                "confidence": 0.94,
            },
            "current_stage": {
                "section": "Current stage",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Pilot-Ready Prototype & COP31 Antalya Active Engagement (Startup Zone / Climate Finance Hub)",
                "source": "GreenHope Status Log",
                "confidence": 0.96,
            },
            "business_model": {
                "section": "Business model",
                "classification": "LEVEL_2_INTERNAL",
                "value": "B2G / B2B SaaS + MRV analytics licensing for municipalities and green-finance institutions, plus project-preparation & impact-verification fee layer for blended climate finance pipelines.",
                "source": "GreenHope Business Model Canvas (Internal)",
                "confidence": 0.90,
            },
            "revenue_model": {
                "section": "Revenue model",
                "classification": "LEVEL_2_INTERNAL",
                "value": "Recurring annual municipal/enterprise platform subscriptions + verified MRV reporting modules tied to green loans/bonds.",
                "source": "GreenHope Commercial Plan (Internal)",
                "confidence": 0.88,
            },
            "annual_revenue": {
                "section": "Annual revenue",
                "classification": "LEVEL_2_INTERNAL",
                "value": None,
                "source": "NOT YET PROVIDED — Founder must confirm audited/current revenue",
                "confidence": 0.0,
            },
            "ip_status": {
                "section": "IP status",
                "classification": "LEVEL_3_CONFIDENTIAL",
                "value": "[CONFIDENTIAL — BLOCKED FROM AUTO-SUBMIT] Proprietary KAG+MRV sensor-fusion algorithms, urban emissions scoring weights, and patent-pending pipeline architecture.",
                "source": "GreenHope IP Register (Level 3)",
                "confidence": 0.95,
            },
            "open_source_policy": {
                "section": "Open-source policy",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Selective open standards for public climate transparency & MRV schemas; core predictive AI models and proprietary algorithms remain closed/protected IP.",
                "source": "GreenHope Governance Policy",
                "confidence": 0.94,
            },
            "partners": {
                "section": "Partners",
                "classification": "LEVEL_2_INTERNAL",
                "value": "Active COP31 Antalya engagement across Startup Zone, Climate Finance Hub, Turkish municipal sustainability stakeholders, and climate finance working groups.",
                "source": "GreenHope COP31 Partnership Tracker",
                "confidence": 0.91,
            },
            "evidence": {
                "section": "Evidence",
                "classification": "LEVEL_1_PUBLIC",
                "value": "Working GreenHope live prototype, verified COP31 investor intelligence database, structured MRV impact methodology, and documented Antalya urban pilot design.",
                "source": "GreenHope Evidence Pack",
                "confidence": 0.93,
            },
            "metrics": {
                "section": "Metrics",
                "classification": "LEVEL_2_INTERNAL",
                "value": "Target pilot KPIs: 15–25% urban waste sorting/diversion uplift, real-time air-quality coverage across pilot districts, ISO/MRV-ready quarterly tCO2e & resilience reporting.",
                "source": "GreenHope Pilot KPI Targets",
                "confidence": 0.89,
            },
            "financial_model": {
                "section": "Financial model",
                "classification": "LEVEL_2_INTERNAL",
                "value": "Phased capital plan: Phase 1 Pilot ($50K–$250K catalytic grant/pilot finance) -> Phase 2 Multi-City Türkiye Rollout ($1M–$3M blended DFI/bank finance) -> Phase 3 Regional Scaling.",
                "source": "GreenHope Financial Model v1",
                "confidence": 0.92,
            },
            "restricted_secrets": {
                "section": "Credentials / Patents / Private Comms",
                "classification": "LEVEL_4_RESTRICTED",
                "value": "[RESTRICTED — NEVER EXPOSED TO AI OR EXTERNAL FORMS] Vault master keys, API tokens, unfiled patent disclosures, personal founder IDs, private investor emails.",
                "source": "Security Officer Vault Policy",
                "confidence": 1.0,
            },
        },
        "kag_domains": [
            "climate resilience",
            "air quality",
            "waste",
            "AI",
            "cities",
            "climate finance",
            "MRV",
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")
    return master


# Detailed verified COP31 claims & event details for the First 10 P1 Knowledge Packs
PACK_SPECIFIC_DETAILS: Dict[str, Dict[str, Any]] = {
    "bbva": {
        "investor_id": "inv_bbva_group",
        "cop31_events": (
            "- **COP31 Global Banking Partner Pavilion (Green Zone — Climate Finance Hub, 400 m²)**: Hosting 60+ sessions on mobilizing climate finance, cleantech scale-up, electrification, resilience, and nature.\n"
            "- **Private Transition Finance & Institutional Capital Roundtables**: Convening businesses, institutional investors, and public entities to bridge innovation-to-investment.\n"
            "- **COP31 Global Finance Summit Participation**: Joining World Bank, EBRD, and GFANZ on unlocking private capital."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** BBVA & Garanti BBVA Pavilion, Climate Finance Hub, Green Zone, Antalya Expo Center\n"
            "- **Target Desk:** BBVA Global Sustainability & CIB Cleantech / Transition Finance Desk\n"
            "- **Approach Strategy:** Present GreenHope's `city pilot -> measurable climate impact -> financing -> scale` model; request intro to BBVA Sustainability / Cleantech innovation team."
        ),
        "verified_claims": [
            {
                "claim": "BBVA Group is an Official Global Banking Partner of UNFCCC COP31 in Antalya with a 400m² Green Zone pavilion hosting 60+ climate finance sessions.",
                "source": "BBVA Official Press Release",
                "url": "https://www.bbva.com/en/sustainability/bbva-to-be-the-global-banking-partner-of-the-united-nations-climate-summit-cop31-in-turkiye/",
                "date_verified": "2026-11-15",
                "confidence": 0.99,
                "status": "verified",
            },
            {
                "claim": "BBVA targets €700 billion in sustainable business (2025–2029), having mobilized €170 billion by Q1 2026 (€36B in Q1 2026 alone).",
                "source": "BBVA Sustainability & Garanti BBVA COP31 Release",
                "url": "https://www.garantibbva.com.tr/en/corporate-communications/cop31-climate-change-summit",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
            {
                "claim": "BBVA explicitly emphasizes bridging the gap between innovation and investment to deploy clean technologies in real-world conditions.",
                "source": "BBVA COP31 Sustainability Statement (Javier Rodríguez Soler)",
                "url": "https://www.bbva.com/en/sustainability/javier-rodriguez-soler-climate-finance-will-be-at-the-heart-of-discussions-at-cop31/",
                "date_verified": "2026-11-15",
                "confidence": 0.97,
                "status": "verified",
            },
            {
                "claim": "BBVA is listed in the COP31 Business Forum Climate Finance & Investments Working Group.",
                "source": "COP31 Business Forum Working Group Paper",
                "url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "garanti_bbva": {
        "investor_id": "inv_garanti_bbva",
        "cop31_events": (
            "- **Joint BBVA / Garanti BBVA Green Zone Pavilion (Climate Finance Hub)**: 60+ sessions on clean energy, decarbonization, water management, carbon markets & just transition.\n"
            "- **Turkish Local Implementation & SME/Corporate Meetings**: Led by Garanti BBVA CEO Mahmut Akten and Sustainability leadership."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** Garanti BBVA & BBVA Pavilion, Climate Finance Hub, Green Zone, Antalya\n"
            "- **Target Desk:** Garanti BBVA Sustainability & Sustainable Finance Advisory / Corporate & SME Transition Desk\n"
            "- **Approach Strategy:** Pitch Antalya/Türkiye municipal & SME pilot alignment; verify green transition credit / strategic pilot sponsorship pathways."
        ),
        "verified_claims": [
            {
                "claim": "Garanti BBVA serves alongside BBVA Group as Official Global Banking Partner of COP31 in Antalya.",
                "source": "Garanti BBVA Official COP31 Page",
                "url": "https://www.garantibbva.com.tr/en/corporate-communications/cop31-climate-change-summit",
                "date_verified": "2026-11-15",
                "confidence": 0.99,
                "status": "verified",
            },
            {
                "claim": "Garanti BBVA raised its sustainable finance target to TRY 3.5 trillion for 2018–2029, surpassing TRY 1 trillion by January 2026.",
                "source": "Garanti BBVA Official COP31 Page",
                "url": "https://www.garantibbva.com.tr/en/corporate-communications/cop31-climate-change-summit",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "aiib": {
        "investor_id": "inv_aiib",
        "cop31_events": (
            "- **IMMEDIATE PRIORITY — TOMORROW, NOVEMBER 16, 2026 (Antalya)**: AIIB COP31 program focused on `policy -> technical support -> project preparation -> public/private financing -> investment-ready climate infrastructure`.\n"
            "- **Nov 12, 2026**: Signed record **$1.6B Climate Policy-Based Financing** with Türkiye + **$300M via Turk Eximbank** ($1.9B total).\n"
            "- **Nov 14, 2026**: Deepened **AIIB–GGGI Cooperation** on project preparation, investment-ready pipelines, co-financing & technical assistance."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** Joint MDB Pavilion & AIIB Nov 16 Antalya Sessions\n"
            "- **Target Desk:** AIIB Project Preparation Special Fund (PPSF) / Public & Private Climate Infrastructure Team + GGGI Joint Liaison\n"
            "- **Approach Strategy:** Do NOT pitch a raw startup grant; position GreenHope as a **city climate-resilience & MRV project-preparation / investment-readiness pilot** linked to AIIB–GGGI & Türkiye's $1.6B climate reform milestones."
        ),
        "verified_claims": [
            {
                "claim": "AIIB signed a record $1.6 billion climate policy-based financing package with Türkiye at COP31 on Nov 12, 2026, plus $300 million via Turk Eximbank.",
                "source": "AIIB / Türkiye Today / Open Press",
                "url": "https://www.turkiyetoday.com/business/turkiye-clinches-51b-in-climate-financing-deals-at-cop31-3232234",
                "date_verified": "2026-11-15",
                "confidence": 0.99,
                "status": "verified",
            },
            {
                "claim": "AIIB and GGGI agreed on Nov 14, 2026 at COP31 in Antalya to deepen cooperation on climate-resilient infrastructure project preparation, investment-ready pipelines, and technical assistance.",
                "source": "AIIB Official Newsroom",
                "url": "https://www.aiib.org/en/news-events/news/2026/aiib-and-gggi-deepen-cooperation-climate-resilient-infrastructure-green-development.html",
                "date_verified": "2026-11-15",
                "confidence": 0.99,
                "status": "verified",
            },
            {
                "claim": "AIIB hosts dedicated COP31 Antalya programming on November 16, 2026 connecting climate finance, project preparation, and smart green resilient infrastructure.",
                "source": "AIIB at COP31 Official Page",
                "url": "https://www.aiib.org/en/news-events/events/2026/aiib-at-cop31.html",
                "date_verified": "2026-11-15",
                "confidence": 0.97,
                "status": "verified",
            },
        ],
    },
    "world_bank": {
        "investor_id": "inv_world_bank_ibrd",
        "cop31_events": (
            "- **World Bank Group at COP31 Antalya**: Signed 3 Türkiye agreements worth **$1.5B** (cities, agriculture, industry) bringing Türkiye portfolio to $32B.\n"
            "- **COP31 Global Finance Summit**: Co-hosted with EBRD, Bloomberg Philanthropies, and GFANZ (with BBVA & major banks).\n"
            "- **Electrify Now Finance Coalition & TIDIP**: Co-leading capital mobilization, guarantees & private-sector pathways via IBRD/IFC/MIGA."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** Joint MDB Pavilion & World Bank Group COP31 Sessions\n"
            "- **Target Desk:** World Bank Türkiye Urban Resilience Program / IFC Climate Tech & Private Sector / MIGA Guarantees\n"
            "- **Approach Strategy:** Ask: *Which World Bank Group instrument, municipal intermediary, country program, or IFC/MIGA pathway can finance a GreenHope city pilot?*"
        ),
        "verified_claims": [
            {
                "claim": "World Bank Group announced three COP31 Türkiye financing agreements worth $1.5 billion supporting cities, agriculture, and industry.",
                "source": "TRT World / Türkiye Today",
                "url": "https://www.trtworld.com/article/08c7af154347",
                "date_verified": "2026-11-15",
                "confidence": 0.99,
                "status": "verified",
            },
            {
                "claim": "World Bank Group's COP31 program centers on financing, knowledge, guarantees, and private-capital mobilization alongside EBRD, BBVA, and GFANZ.",
                "source": "World Bank Group COP31 Campaign",
                "url": "https://www.worldbank.org/en/who-we-are/news/campaigns/2026/the-world-bank-group-at-cop31",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "qnb": {
        "investor_id": "inv_qnb_turkiye",
        "cop31_events": (
            "- **COP31 Sustainable Financing Signings**: QNB Türkiye secured up to **$500M** in sustainable finance arrangements at COP31, including a **€75M Proparco renewable energy leasing deal** (>€250M in 2026).\n"
            "- **COP31 Business Forum Climate Finance & Investments Working Group**: Active bank participant."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** Green Zone Climate Finance Hub / Business Forum\n"
            "- **Target Desk:** QNB Türkiye Sustainability & Green Finance / QNBeyond Innovation & Leasing Desk\n"
            "- **Approach Strategy:** Target green SME/equipment financing for GreenHope IoT sensor hardware + municipal/enterprise deployment."
        ),
        "verified_claims": [
            {
                "claim": "QNB Türkiye secured up to $500M in sustainable financing arrangements at COP31, including a €75M Proparco solar & wind leasing agreement.",
                "source": "Anadolu Agency / UA.NEWS / Asi Gazetesi",
                "url": "https://www.asigazetesi.com/iklim-zirvesi-cop31-antalya-qnb-leasing-ile-proparcodan-75-milyon-avroluk-surdurulebilir-enerji-anlasmasi",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
            {
                "claim": "QNB Bank is listed in the COP31 Business Forum Climate Finance & Investments Working Group.",
                "source": "COP31 Business Forum Working Group Paper",
                "url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "meridiam": {
        "investor_id": "inv_meridiam",
        "cop31_events": (
            "- **COP31 Business Forum Climate Finance & Investments Working Group**: Representing long-term sustainable urban infrastructure & resilience investment.\n"
            "- **Focus Themes**: Municipal PPPs, resilient cities, clean mobility, circular waste infrastructure & verified SDG impact."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** COP31 Business Forum & Climate Finance Networking Sessions\n"
            "- **Target Desk:** Meridiam Urban Resilience / Sustainability & Impact Infrastructure Origination\n"
            "- **Approach Strategy:** Pitch GreenHope as an urban resilience & MRV intelligence layer enhancing bankability and SDG impact verification for Meridiam city infrastructure assets."
        ),
        "verified_claims": [
            {
                "claim": "Meridiam is a confirmed institutional infrastructure investor listed in the COP31 Business Forum Climate Finance & Investments Working Group.",
                "source": "COP31 Business Forum Working Group Paper",
                "url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "m_and_g": {
        "investor_id": "inv_m_and_g",
        "cop31_events": (
            "- **COP31 Business Forum Climate Finance & Investments Working Group**: Representing institutional climate asset management & private impact capital.\n"
            "- **Focus Themes**: Scalable climate innovation, measurable impact investing & emerging-market transition capital."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** COP31 Business Forum / Institutional Investor Meetings\n"
            "- **Target Desk:** M&G Catalyst / Sustainability & Impact Investing Team\n"
            "- **Approach Strategy:** Highlight GreenHope's defensible AI + MRV data moat, scalable municipal SaaS economics, and verified climate KPIs."
        ),
        "verified_claims": [
            {
                "claim": "M&G is listed as an institutional asset manager & investor in the COP31 Business Forum Climate Finance & Investments Working Group.",
                "source": "COP31 Business Forum Working Group Paper",
                "url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "hsbc": {
        "investor_id": "inv_hsbc",
        "cop31_events": (
            "- **COP31 Antalya Delegation (19 delegates)** & **COP31 Business Forum Climate Finance & Investments Working Group (HSBC / HSBC Türkiye)**.\n"
            "- **Focus Themes**: Transition finance, green trade, sustainable supply-chain MRV & climate asset management."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** COP31 Business Forum / Blue & Green Zone Finance Meetings\n"
            "- **Target Desk:** HSBC Türkiye Sustainable Finance & Global Climate Tech / Transition Advisory\n"
            "- **Approach Strategy:** Position GreenHope's MRV verification for corporate/industrial green supply chains & municipal resilience."
        ),
        "verified_claims": [
            {
                "claim": "HSBC / HSBC Türkiye participates in the COP31 Business Forum Climate Finance & Investments Working Group and maintains a 19-member COP31 Antalya delegation.",
                "source": "COP31 Business Forum WG & COP31 Delegation Report",
                "url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "akbank": {
        "investor_id": "inv_akbank",
        "cop31_events": (
            "- **Akbank COP31 Green Zone Stand & Panels (Nov 9–20)**: TRY 2.5 trillion sustainable finance target by 2030.\n"
            "- **Nov 15 (Today)**: Akbank + GEFF Türkiye green business transformation session.\n"
            "- **Nov 16 (Tomorrow)**: Circular economy, waste-to-economic-value, industrial greening & inclusive transition panel."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** Akbank Stand, Green Zone, Antalya Expo Center\n"
            "- **Target Desk:** Akbank Sustainable Finance / GEFF Türkiye / Akbank LAB Innovation Desk\n"
            "- **Approach Strategy:** Attend Akbank's Nov 16 circular economy & waste-to-value panel—direct alignment with GreenHope's smart waste & circularity AI."
        ),
        "verified_claims": [
            {
                "claim": "Akbank announced its COP31 Antalya program implementing a TRY 2.5 trillion sustainable finance target through 2030 with GEFF Türkiye, KGF, sustainable agriculture, and circular economy panels.",
                "source": "Akbank COP31 Press Coverage (Başak Gazetesi / Ekonomi Politikası)",
                "url": "https://basakgazetesi.com/haber/akbank-cop31-icin-kapsamli-iklim-finansmani-ve-donusum-programini-acikladi-897587",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
            {
                "claim": "Akbank is listed in the COP31 Business Forum Climate Finance & Investments Working Group.",
                "source": "COP31 Business Forum Working Group Paper",
                "url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
    "denizbank": {
        "investor_id": "inv_denizbank",
        "cop31_events": (
            "- **COP31 Business Forum Climate Finance & Investments Working Group**: Representing Turkish commercial, agricultural, tourism & innovation banking (Emirates NBD Group).\n"
            "- **Local Antalya Regional Strength**: Major Mediterranean footprint across Antalya municipalities, agriculture, and Deniz Ventures climate-tech."
        ),
        "contacts": (
            "- **On-Site COP31 Location:** COP31 Business Forum / Green Zone Finance Hub\n"
            "- **Target Desk:** DenizBank Sustainability, Municipal Banking & Deniz Ventures\n"
            "- **Approach Strategy:** Leverage Antalya host-city connection for a local GreenHope municipal/agri-resilience pilot co-financed via DenizBank/KGF or Deniz Ventures."
        ),
        "verified_claims": [
            {
                "claim": "DenizBank is listed as a Turkish banking participant in the COP31 Business Forum Climate Finance & Investments Working Group.",
                "source": "COP31 Business Forum Working Group Paper",
                "url": "https://www.copbusiness.org/papers/COP31_WG_climate-finance-investments.pdf",
                "date_verified": "2026-11-15",
                "confidence": 0.98,
                "status": "verified",
            },
        ],
    },
}


def build_ten_investor_knowledge_packs(investors: List[InvestorRecord], packs_root: Path) -> List[dict]:
    """Generate the exact 13-file Investor Knowledge Pack folder structure for all 10 P1 priority targets."""
    packs_root.mkdir(parents=True, exist_ok=True)
    by_id = {inv.investor_id: inv for inv in investors}
    index_summary: List[dict] = []

    standard_questions = [
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

    for slug, spec in PACK_SPECIFIC_DETAILS.items():
        inv = by_id[spec["investor_id"]]
        pdir = packs_root / slug
        ev_dir = pdir / "evidence"
        ev_dir.mkdir(parents=True, exist_ok=True)

        (pdir / "identity.md").write_text(
            f"# {inv.name} (`{inv.investor_id}`)\n\n"
            f"- **Short Name:** {inv.short_name}\n"
            f"- **Category:** {inv.category.value}\n"
            f"- **Ecosystem Branch:** {inv.ecosystem_branch.value}\n"
            f"- **Verification / Relationship Status:** `{inv.relationship_status.value}`\n"
            f"- **Priority Tier:** `{inv.priority_tier}` | **AI/RAG Priority:** `{inv.ai_rag_priority}`\n"
            f"- **GreenHope Relevance:** `{inv.greenhope_relevance}`\n"
            f"- **Headquarters:** {inv.hq_country}\n"
            f"- **Official Portal:** {inv.application_portal_url}\n",
            encoding="utf-8",
        )
        (pdir / "climate_strategy.md").write_text(
            f"# {inv.short_name} — COP31 Climate Strategy\n\n"
            f"## COP31 Antalya 2026 Role\n{inv.cop31_antalya_role}\n\n"
            f"## Verified 2026 Commitment\n{inv.cop31_verified_2026_commitment}\n\n"
            f"## Strategic Alignment for GreenHope\n{inv.greenhope_fit_notes}\n",
            encoding="utf-8",
        )
        (pdir / "investment_policy.md").write_text(
            f"# {inv.short_name} — Investment & Exclusion Policy\n\n"
            f"## Mandatory Underwriting / Compliance Requirements\n"
            + "\n".join(f"- {r}" for r in inv.mandatory_form_requirements)
            + "\n\n## Explicit Exclusions\n"
            + ("\n".join(f"- {e}" for e in inv.exclusion_rules) if inv.exclusion_rules else "- Standard Paris-aligned fossil-fuel exclusions apply.")
            + "\n",
            encoding="utf-8",
        )
        (pdir / "eligibility.md").write_text(
            f"# {inv.short_name} — Eligibility Rules\n\n"
            f"- **Eligible Applicant Types:** {', '.join(inv.eligible_applicant_types)}\n"
            f"- **Geographic Mandate:** {', '.join(inv.geographic_focus)}\n"
            f"- **Anti-Hallucination Rule:** Never invent deadlines, grants, or eligibility beyond verified official criteria.\n",
            encoding="utf-8",
        )
        (pdir / "instruments.md").write_text(
            f"# {inv.short_name} — Financing Instruments\n\n"
            + "\n".join(f"- {i}" for i in inv.financing_instruments)
            + "\n",
            encoding="utf-8",
        )
        (pdir / "sectors.md").write_text(
            f"# {inv.short_name} — Priority Climate Sectors\n\n"
            + "\n".join(f"- {s}" for s in inv.target_sectors)
            + "\n",
            encoding="utf-8",
        )
        (pdir / "geography.md").write_text(
            f"# {inv.short_name} — Geographic Focus\n\n"
            + "\n".join(f"- {g}" for g in inv.geographic_focus)
            + "\n",
            encoding="utf-8",
        )
        (pdir / "ticket_size.md").write_text(
            f"# {inv.short_name} — Typical Ticket Size\n\n"
            f"- **Minimum Typical Ticket:** USD {inv.typical_ticket_min_usd:,.0f}\n"
            f"- **Maximum Typical Ticket:** USD {inv.typical_ticket_max_usd:,.0f}\n"
            f"- **Note for GreenHope Pilots:** For smaller pilot tranches ($50K–$250K), explore technical assistance, innovation hubs, or municipal/intermediary on-lending facilities.\n",
            encoding="utf-8",
        )
        (pdir / "application_process.md").write_text(
            f"# {inv.short_name} — Application Process & Human-in-the-Loop Workflow\n\n"
            f"- **Form Template:** `{inv.form_template_type.value}`\n"
            f"- **Official Portal:** {inv.application_portal_url}\n"
            f"- **Mandatory Safeguard:** `AUTO-FILL -> REVIEW -> APPROVE -> SUBMIT`. Never auto-submit Level 3 (Confidential) or Level 4 (Restricted) GreenHope IP.\n",
            encoding="utf-8",
        )
        (pdir / "application_questions.json").write_text(
            json.dumps(
                {
                    "investor_id": inv.investor_id,
                    "investor_name": inv.name,
                    "knowledge_pack_slug": slug,
                    "form_template_type": inv.form_template_type.value,
                    "questions": standard_questions,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (pdir / "contacts.md").write_text(f"# {inv.short_name} — COP31 Contact & Approach Strategy\n\n{spec['contacts']}\n", encoding="utf-8")
        (pdir / "cop31_events.md").write_text(f"# {inv.short_name} — COP31 Antalya (Nov 2026) Events & Milestones\n\n{spec['cop31_events']}\n", encoding="utf-8")
        (ev_dir / "verified_claims.json").write_text(
            json.dumps(
                {
                    "investor_id": inv.investor_id,
                    "knowledge_pack_slug": slug,
                    "claims": spec["verified_claims"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        index_summary.append(
            {
                "slug": slug,
                "investor_id": inv.investor_id,
                "investor_name": inv.name,
                "priority_tier": inv.priority_tier,
                "ai_rag_priority": inv.ai_rag_priority,
                "relationship_status": inv.relationship_status.value,
                "verified_claims_count": len(spec["verified_claims"]),
                "files": sorted(str(p.relative_to(pdir)) for p in pdir.rglob("*") if p.is_file()),
            }
        )

    (packs_root / "packs_index.json").write_text(
        json.dumps({"total_packs": len(index_summary), "packs": index_summary}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return index_summary
