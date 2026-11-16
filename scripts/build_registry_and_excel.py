"""Builds the verified COP31 Antalya (Nov 2026) Investor & Bank Registry in JSON, CSV, and formatted Excel (.xlsx),
plus 3 multi-sector sample applicant project profiles for testing the KAG/RAG form-filling pipeline.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import List

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.forms.form_templates import FORM_TEMPLATES
from src.models.schemas import (
    AIModelArchitecture,
    FormTemplateType,
    InvestorCategory,
    InvestorRecord,
)
from scripts.build_greenhope_knowledge_packs import (
    enrich_investor_record,
    get_additional_v1_and_ecosystem_entities,
)


def get_verified_cop31_investors() -> List[InvestorRecord]:
    """40 verified real banks, MDBs, DFIs, multilateral climate funds & institutional investors active at COP31 Antalya (Nov 9-20, 2026)."""
    raw_items = [
        # =====================================================================
        # CATEGORY 1: MULTILATERAL DEVELOPMENT BANKS (MDBs) — 9 Institutions
        # =====================================================================
        {
            "investor_id": "inv_world_bank_ibrd",
            "name": "World Bank Group (IBRD / IDA)",
            "short_name": "World Bank",
            "category": InvestorCategory.MDB,
            "hq_country": "United States (Multilateral)",
            "geographic_focus": ["Global", "Emerging Markets", "Developing Countries", "Türkiye", "Africa", "Asia", "Latin America"],
            "cop31_antalya_role": "Signed $1.5B in 3 COP31 agreements in Türkiye; Co-Chair of Electrify Now Finance Coalition; TIDIP founding member; Global Finance Summit co-host",
            "cop31_verified_2026_commitment": "$1.5B in 3 COP31 Türkiye deals (cities, agriculture, industry; €209.2M via Turk Eximbank; $32B Türkiye portfolio) + $100M Brazil forest restoration with BNDES",
            "financing_instruments": ["Sovereign Loan", "Policy-Based Financing", "Credit Guarantee", "Concessional Credit (IDA)", "Blended Finance"],
            "typical_ticket_min_usd": 20_000_000,
            "typical_ticket_max_usd": 1_000_000_000,
            "target_sectors": ["Electrification & Grid", "Industrial Decarbonization", "Climate Adaptation & Resilience", "Sustainable Agriculture & Water", "Resilient Cities & Infrastructure"],
            "eligible_applicant_types": ["Sovereign/Government", "Municipality", "Financial Intermediary", "State-Owned Enterprise"],
            "application_portal_url": "https://www.worldbank.org/en/topic/climatechange",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "Joint MDB Paris Alignment Assessment (BB1 Mitigation & BB2 Adaptation)",
                "World Bank Environmental and Social Framework (ESF) & EIA clearance",
                "Sovereign/Treasury guarantee or government counterpart endorsement",
                "Host-country NDC & Climate Law alignment",
            ],
            "exclusion_rules": ["Unabated coal power generation", "Upstream oil & gas exploration"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Strict multi-hop sovereign eligibility, ESF risk categorization, NDC/Paris BB1-BB2 rules, and Treasury guarantee logic require deterministic Knowledge Graph reasoning.",
            "verification_source_url": "https://www.turkiyetoday.com/business/turkiye-clinches-51b-in-climate-financing-deals-at-cop31-3232234",
        },
        {
            "investor_id": "inv_ifc",
            "name": "International Finance Corporation (IFC)",
            "short_name": "IFC",
            "category": InvestorCategory.MDB,
            "hq_country": "United States (Multilateral)",
            "geographic_focus": ["Global", "Emerging Markets", "Developing Countries", "Türkiye", "Africa", "Asia", "Latin America"],
            "cop31_antalya_role": "Founding private-sector partner of Türkiye Industrial Decarbonization Investment Platform (TIDIP) targeting $6B by 2030",
            "cop31_verified_2026_commitment": "Co-anchoring $6B TIDIP mobilization for steel, aluminum, cement & fertilizer decarbonization plus private-sector climate debt/equity",
            "financing_instruments": ["Senior Debt", "Equity", "Mezzanine", "Blended Finance", "Green Bond Anchor", "Risk-Sharing Guarantee"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 250_000_000,
            "target_sectors": ["Industrial Decarbonization", "Renewable Energy", "Energy Storage", "Green Buildings", "Climate-Smart Agriculture", "Circular Economy"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Growth-Stage Private Enterprise"],
            "application_portal_url": "https://www.ifc.org/en/what-we-do/sector-expertise/climate-business",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "IFC Performance Standards (PS 1-8) compliance",
                "Paris Alignment & GHG emissions accounting",
                "Commercial bankability & audited financials",
                "Private-sector ownership (>50% private or commercially managed)",
            ],
            "exclusion_rules": ["New coal-fired power", "Unabated fossil fuel projects", "IFC Exclusion List activities"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "Combines KAG for strict IFC Performance Standards, ownership & exclusion checks with RAG for commercial additionality and TIDIP sector narratives.",
            "verification_source_url": "https://www.riotimesonline.com/turkey-eyes-6-billion-green-industry-cop31-antalya/",
        },
        {
            "investor_id": "inv_ebrd",
            "name": "European Bank for Reconstruction and Development (EBRD)",
            "short_name": "EBRD",
            "category": InvestorCategory.MDB,
            "hq_country": "United Kingdom (Multilateral)",
            "geographic_focus": ["Türkiye", "Europe", "Central Asia", "MENA", "Sub-Saharan Africa", "Emerging Markets"],
            "cop31_antalya_role": "Co-host of COP31 Global Finance Summit; Joint MDB Pavilion; TIDIP partner; Electrify Now Finance Coalition; GEFF Türkiye",
            "cop31_verified_2026_commitment": "Green Economy Transition (GET) Strategy 2026–2030; €26B+ cumulative commitments in Türkiye; TIDIP & Kazakhstan JETP partner",
            "financing_instruments": ["Senior Debt", "Equity", "Subordinated Debt", "Green Credit Lines (GEFF)", "Blended Concessional Finance", "Technical Assistance"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Renewable Energy", "Electrification & Grid", "Industrial Decarbonization", "Climate Adaptation & Resilience", "Green Cities & Mobility", "SME Green Transition"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Municipality", "Financial Intermediary", "SME"],
            "application_portal_url": "https://www.ebrd.com/work-with-us/project-finance.html",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "EBRD Green Economy Transition (GET) & Paris Alignment assessment",
                "EBRD Environmental and Social Policy (PR 1-10) & EIA permits",
                "Sound banking principles & transition impact demonstration",
                "Integrity & KYC beneficial ownership disclosure",
            ],
            "exclusion_rules": ["Thermal coal mining or coal-fired power", "Upstream oil exploration"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "GET 2026-30 taxonomy rules, country-of-operation constraints, and 10 Performance Requirements map directly to deterministic multi-hop KAG reasoning.",
            "verification_source_url": "https://www.ebrd.com/home/news-and-events/news/events/ebrd-at-cop-31.html",
        },
        {
            "investor_id": "inv_eib_eif",
            "name": "European Investment Bank (EIB) & European Investment Fund (EIF)",
            "short_name": "EIB Group",
            "category": InvestorCategory.MDB,
            "hq_country": "Luxembourg (EU Multilateral)",
            "geographic_focus": ["Europe", "EU", "Türkiye", "Global", "Emerging Markets", "Africa", "Mediterranean"],
            "cop31_antalya_role": "Launched Climate Adaptation Plan Phase 2 at COP31; signed EIB-İLBANK advisory deal Nov 13; TIDIP signatory; Electrify Now Coalition",
            "cop31_verified_2026_commitment": "≥€30B Climate Adaptation Plan Phase 2 (2026–2030); €20B Global Green Bond Initiative; EIF €80B European Tech Champions scale-up alliance; €31B cumulative in Türkiye",
            "financing_instruments": ["Long-Term Investment Loan", "Framework Loan", "Green Bond Anchor", "Venture Debt / EIF Equity Guarantee", "Technical Assistance (Gap Fund)"],
            "typical_ticket_min_usd": 15_000_000,
            "typical_ticket_max_usd": 500_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Renewable Energy", "Electrification & Grid", "Resilient Cities & Infrastructure", "Industrial Decarbonization", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Large Corporate", "Municipality", "Sovereign/Government", "Financial Intermediary", "Project SPV", "Climate-Tech Startup"],
            "application_portal_url": "https://www.eib.org/en/products/index.htm",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "EIB Climate Bank Roadmap & Paris Alignment compliance",
                "EU Taxonomy alignment or Climate Adaptation Plan Phase 2 criteria",
                "Environmental Impact Assessment (EU EIA Directive equivalent)",
                "Economic & financial viability appraisal (typically financing up to 50% of project cost)",
            ],
            "exclusion_rules": ["Unabated fossil fuel energy projects (oil, gas, coal)"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Strict 50% co-financing cap, EU Taxonomy alignment rules, and EIB vs. EIF subsidiary routing are best enforced via structured KAG logic.",
            "verification_source_url": "https://www.eib.org/en/press/all/2026-416-eib-group-to-showcase-new-climate-finance-actions-at-cop31",
        },
        {
            "investor_id": "inv_adb",
            "name": "Asian Development Bank (ADB)",
            "short_name": "ADB",
            "category": InvestorCategory.MDB,
            "hq_country": "Philippines (Multilateral)",
            "geographic_focus": ["Asia", "Asia-Pacific", "Central Asia", "Türkiye"],
            "cop31_antalya_role": "Signed $1.19B+ COP31 Türkiye deals (resilient hospitals & VakıfBank SME line); joined TIDIP; MDB Adaptation Partnership; coal phase-out",
            "cop31_verified_2026_commitment": "€620M ($687M) disaster-resilient hospitals + $500M via VakıfBank for SMEs & women entrepreneurs (total $3.1B Türkiye support)",
            "financing_instruments": ["Sovereign Loan", "Non-Sovereign Debt", "Equity", "Guarantee", "Blended Concessional Finance", "Technical Assistance Grant"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 500_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Renewable Energy", "Industrial Decarbonization", "SME Green Transition", "Resilient Infrastructure & Health", "Energy Transition"],
            "eligible_applicant_types": ["Sovereign/Government", "Large Corporate", "Financial Intermediary", "Project SPV", "Municipality"],
            "application_portal_url": "https://www.adb.org/work-with-us/private-sector-financing",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "ADB Paris Alignment screening (BB1 & BB2)",
                "ADB Safeguard Policy Statement (Environment, Involuntary Resettlement, Indigenous Peoples)",
                "Member country eligibility & development impact indicators",
                "Financial & Integrity Due Diligence",
            ],
            "exclusion_rules": ["Coal mining and coal-fired power generation", "Upstream oil & gas exploration"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "Uses KAG for ADB member-country & safeguard rules and RAG for sector-specific resilience, gender inclusion, and coal-transition narratives.",
            "verification_source_url": "https://www.trtworld.com/article/08c7af154347",
        },
        {
            "investor_id": "inv_aiib",
            "name": "Asian Infrastructure Investment Bank (AIIB)",
            "short_name": "AIIB",
            "category": InvestorCategory.MDB,
            "hq_country": "China (Multilateral)",
            "geographic_focus": ["Asia", "Türkiye", "EMEA", "Global", "Emerging Markets", "Central Asia"],
            "cop31_antalya_role": "Signed record $1.9B COP31 Türkiye climate package (its largest climate policy-based financing to date)",
            "cop31_verified_2026_commitment": "$1.6B Türkiye Climate Action Program (1,800 MW wind/solar, 225,000 farmers, 50,000 ha carbon sinks) + $300M via Turk Eximbank ($7.47B climate finance in 2025)",
            "financing_instruments": ["Sovereign Loan", "Climate Policy-Based Financing", "Non-Sovereign Infrastructure Debt", "Equity", "Guarantee"],
            "typical_ticket_min_usd": 20_000_000,
            "typical_ticket_max_usd": 600_000_000,
            "target_sectors": ["Renewable Energy", "Electrification & Grid", "Industrial Decarbonization", "Sustainable Agriculture & Water", "Climate Adaptation & Resilience", "Carbon Sinks & Nature"],
            "eligible_applicant_types": ["Sovereign/Government", "Large Corporate", "Project SPV", "Financial Intermediary", "Municipality"],
            "application_portal_url": "https://www.aiib.org/en/projects/propose/index.html",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "AIIB Paris Alignment & Climate Finance Classification",
                "Environmental and Social Framework (ESF) & EIA permits",
                "Infrastructure connectivity & green transition mandate fit",
                "Procurement & financial sustainability assessment",
            ],
            "exclusion_rules": ["Coal-fired power plants and coal mining infrastructure"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Policy milestones, sovereign vs. non-sovereign infrastructure rules, and ESF screening rely on structured KAG constraint verification.",
            "verification_source_url": "https://theopenpress.in/article/aiib-turkiye-record-1-6-billion-climate-deal-cop31-antalya",
        },
        {
            "investor_id": "inv_isdb",
            "name": "Islamic Development Bank (IsDB)",
            "short_name": "IsDB",
            "category": InvestorCategory.MDB,
            "hq_country": "Saudi Arabia (Multilateral)",
            "geographic_focus": ["OIC Member Countries", "Türkiye", "MENA", "Africa", "Asia", "Central Asia", "Emerging Markets"],
            "cop31_antalya_role": "Joined Türkiye Industrial Decarbonization Investment Platform (TIDIP) Nov 12 at COP31; signatory to Türkiye $5.1B MDB deals",
            "cop31_verified_2026_commitment": "Strategic partner to $6B TIDIP industrial decarbonization coalition + part of Türkiye's $5.1B COP31 MDB financing package",
            "financing_instruments": ["Shariah-Compliant Istisna'a", "Murabaha", "Ijarah Leasing", "Green Sukuk", "Concessional Loan", "Technical Assistance"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Industrial Decarbonization", "Renewable Energy", "Climate Adaptation & Resilience", "Sustainable Agriculture & Water", "Resilient Infrastructure"],
            "eligible_applicant_types": ["Sovereign/Government", "Large Corporate", "Financial Intermediary", "Project SPV"],
            "application_portal_url": "https://www.isdb.org/what-we-do/climate-change",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "Shariah-compliant financing structure (no riba/interest; Istisna'a, Murabaha, Ijarah, or Sukuk)",
                "OIC member country eligibility",
                "Joint MDB Paris Alignment & Environmental/Social Safeguards",
                "Climate resilience & green industrial transition alignment",
            ],
            "exclusion_rules": ["Interest-bearing non-Shariah structures", "Thermal coal", "Non-Shariah prohibited industries"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Hard Shariah-compliance structuring constraints + OIC country membership rules make KAG graph validation indispensable to prevent non-compliant drafts.",
            "verification_source_url": "https://www.isdb.org/news/at-cop31-in-antalya-islamic-development-bank-joins-turkiye-industrial-decarbonization-investment-platform-tidip",
        },
        {
            "investor_id": "inv_afdb",
            "name": "African Development Bank Group (AfDB)",
            "short_name": "AfDB",
            "category": InvestorCategory.MDB,
            "hq_country": "Côte d'Ivoire (Multilateral)",
            "geographic_focus": ["Africa", "Sub-Saharan Africa", "North Africa"],
            "cop31_antalya_role": "Co-Chair of Electrify Now Finance Coalition (35-by-35 Pledge); Africa Pavilion (A240); launched RESILAFRICA food systems flagship",
            "cop31_verified_2026_commitment": "Co-leading global Electrify Now Finance Coalition with World Bank + RESILAFRICA food systems resilience & African climate finance mobilization",
            "financing_instruments": ["Sovereign Loan", "Non-Sovereign Debt", "Equity", "Partial Risk Guarantee", "Concessional Finance (ADF)", "Climate Adaptation Grant"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Electrification & Grid", "Renewable Energy", "Sustainable Agriculture & Water", "Climate Adaptation & Resilience", "Nature-Based Solutions"],
            "eligible_applicant_types": ["Sovereign/Government", "Large Corporate", "Project SPV", "Financial Intermediary", "Municipality"],
            "application_portal_url": "https://www.afdb.org/en/topics-and-sectors/initiatives-partnerships/climate-change",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "African Regional Member Country host jurisdiction",
                "AfDB Integrated Safeguards System (ISS) & EIA",
                "Climate Safeguards System (CSS) & Paris Alignment",
                "Alignment with Electrify Now / RESILAFRICA / African NDCs",
            ],
            "exclusion_rules": ["Coal-fired power generation", "Non-African host projects"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG enforces strict African Regional Member Country & safeguard rules while RAG drafts compelling RESILAFRICA and 35-by-35 electrification narratives.",
            "verification_source_url": "https://www.ipsnews.net/2026/11/cop31-african-development-bank-to-co-lead-global-electrification-finance-initiative/",
        },
        {
            "investor_id": "inv_idb",
            "name": "Inter-American Development Bank (IDB / IDB Invest)",
            "short_name": "IDB Group",
            "category": InvestorCategory.MDB,
            "hq_country": "United States (Multilateral)",
            "geographic_focus": ["Latin America", "Caribbean", "LAC", "Americas"],
            "cop31_antalya_role": "Founding member of Electrify Now Finance Coalition at COP31; signed LOI with BNDES & IBRD for Brazil industrial decarbonization",
            "cop31_verified_2026_commitment": "LOI toward $1B industrial decarbonization package in Brazil (with IBRD/CIF/BNDES) + Electrify Now Finance Coalition",
            "financing_instruments": ["Sovereign Loan", "Private-Sector Debt (IDB Invest)", "Equity", "Blended Finance", "Guarantee", "Green/Blue Bonds"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 400_000_000,
            "target_sectors": ["Industrial Decarbonization", "Electrification & Grid", "Renewable Energy", "Nature-Based Solutions & Forestry", "Climate Adaptation & Resilience"],
            "eligible_applicant_types": ["Sovereign/Government", "Large Corporate", "Project SPV", "Financial Intermediary", "Municipality"],
            "application_portal_url": "https://www.iadb.org/en/who-we-are/topics/climate-change",
            "form_template_type": FormTemplateType.MDB_CONCEPT_NOTE,
            "mandatory_form_requirements": [
                "LAC borrowing member country jurisdiction",
                "IDB Environmental and Social Policy Framework (ESPF) & Paris Alignment",
                "Development effectiveness & additionality scoring (DELTA)",
                "Audited financials & procurement transparency",
            ],
            "exclusion_rules": ["Thermal coal", "Non-LAC project jurisdictions"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG checks LAC regional eligibility and ESPF rules while RAG grounds DELTA development impact and decarbonization narratives.",
            "verification_source_url": "https://carbon-pulse.com/571307/",
        },

        # =====================================================================
        # CATEGORY 2: BILATERAL DFIs & NATIONAL DEVELOPMENT BANKS — 9 Institutions
        # =====================================================================
        {
            "investor_id": "inv_kfw",
            "name": "KfW Development Bank (Germany)",
            "short_name": "KfW",
            "category": InvestorCategory.BILATERAL_DFI,
            "hq_country": "Germany",
            "geographic_focus": ["Global", "Germany", "Europe", "Türkiye", "Emerging Markets", "Developing Countries", "Africa", "Asia"],
            "cop31_antalya_role": "Executive Board delegation at COP31; signed €250M green transition loan with Turk Eximbank; climate mobility & energy panels",
            "cop31_verified_2026_commitment": "€250M COP31 loan with Turk Eximbank + €415B cumulative climate & environmental commitments since 2017",
            "financing_instruments": ["Promotional Loan", "Concessional Development Loan", "Grant (IKI / BMZ)", "Green Credit Line", "Climate Venture Capital"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 350_000_000,
            "target_sectors": ["Renewable Energy", "Urban Mobility & Transport", "Energy Efficiency & Green Buildings", "Biodiversity & Nature", "Industrial Decarbonization", "Climate Adaptation & Resilience"],
            "eligible_applicant_types": ["Sovereign/Government", "Financial Intermediary", "Municipality", "Large Corporate", "Project SPV"],
            "application_portal_url": "https://www.kfw-entwicklungsbank.de/",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "KfW Sustainability Guideline & Environmental/Social Impact Assessment",
                "Paris Agreement compatibility & GHG accounting",
                "Partner-country government or bank intermediary mandate",
                "IFC Performance Standards / EU environmental benchmark",
            ],
            "exclusion_rules": ["Coal power/mining", "Unabated fossil fuel expansion"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG verifies KfW/BMZ mandate & exclusion criteria while RAG draws from KfW's 4-sector climate protection framework (transport, energy, buildings, industry).",
            "verification_source_url": "https://www.kfw.de/About-KfW/Newsroom/Latest-News/S12-Themenseite-3.html",
        },
        {
            "investor_id": "inv_proparco_afd",
            "name": "AFD Group / Proparco (France)",
            "short_name": "Proparco / AFD",
            "category": InvestorCategory.BILATERAL_DFI,
            "hq_country": "France",
            "geographic_focus": ["Emerging Markets", "Developing Countries", "Türkiye", "Africa", "MENA", "Asia", "Latin America"],
            "cop31_antalya_role": "Signed €75M sustainable energy financing deal with QNB Leasing at COP31 Antalya (solar & wind power)",
            "cop31_verified_2026_commitment": "€75M COP31 QNB Leasing renewable energy deal (>€250M total 2026 renewable leasing mobilization with QNB Leasing)",
            "financing_instruments": ["Senior Debt", "Subordinated Debt", "Equity", "Green Credit/Leasing Line", "Guarantee (Choose Africa / EFSD+)", "Technical Assistance"],
            "typical_ticket_min_usd": 3_000_000,
            "typical_ticket_max_usd": 120_000_000,
            "target_sectors": ["Renewable Energy", "Energy Efficiency", "Climate-Smart Agriculture", "Sustainable Cities", "SME Green Transition", "Energy Storage"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Growth-Stage Private Enterprise", "SME"],
            "application_portal_url": "https://www.proparco.fr/en/how-submit-project",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "IFC Performance Standards & Proparco E&S Action Plan",
                "100% Paris-Aligned AFD Group screening",
                "Demonstrated development impact & additionality",
                "Audited financial statements (3 years) or bankable SPV model",
            ],
            "exclusion_rules": ["Coal, upstream oil & gas, heavy fuel oil power"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG checks Proparco ticket bounds, Paris alignment & IFC PS rules while RAG drafts development-impact and technical assistance sections.",
            "verification_source_url": "https://www.asigazetesi.com/iklim-zirvesi-cop31-antalya-qnb-leasing-ile-proparcodan-75-milyon-avroluk-surdurulebilir-enerji-anlasmasi",
        },
        {
            "investor_id": "inv_bii_uk",
            "name": "British International Investment (BII — UK)",
            "short_name": "BII",
            "category": InvestorCategory.BILATERAL_DFI,
            "hq_country": "United Kingdom",
            "geographic_focus": ["Africa", "South Asia", "Asia-Pacific", "Caribbean"],
            "cop31_antalya_role": "Co-launched '10by30' ($10B emerging markets climate finance coalition) at COP31 on Nov 13 with Norfund & FinDev Canada",
            "cop31_verified_2026_commitment": "Co-delivering $10B (€10B) '10by30' emerging markets climate finance by 2030 via British Climate Partners (shared pipeline & DD)",
            "financing_instruments": ["Direct Equity", "Senior/Mezzanine Debt", "Intermediated Fund Investment", "Blended Concessional Finance", "Technical Assistance"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 250_000_000,
            "target_sectors": ["Renewable Energy", "Electrification & Grid", "Energy Storage", "Sustainable Fuels", "Industrial Decarbonization", "Climate Adaptation & Resilience"],
            "eligible_applicant_types": ["Project SPV", "Large Corporate", "Financial Intermediary", "Growth-Stage Private Enterprise", "Climate-Tech Startup"],
            "application_portal_url": "https://www.bii.co.uk/en/work-with-us/",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "10by30 harmonized DFI climate reporting & avoided emissions methodology",
                "BII Policy on Responsible Investing (IFC Performance Standards)",
                "UK FCDO priority emerging market eligibility (Africa, Asia, Caribbean)",
                "Private capital mobilization & commercial viability",
            ],
            "exclusion_rules": ["Coal, oil, unabated fossil-fuel generation"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG verifies 10by30 co-investment eligibility and BII geographic/exclusion rules while RAG synthesizes British Climate Partners mobilization narratives.",
            "verification_source_url": "https://hapakenya.com/2026/11/13/uk-norway-canada-launch-10b-climate-finance-partnership-at-cop31/",
        },
        {
            "investor_id": "inv_norfund",
            "name": "Norfund (Norwegian Investment Fund / Climate Investment Fund)",
            "short_name": "Norfund",
            "category": InvestorCategory.BILATERAL_DFI,
            "hq_country": "Norway",
            "geographic_focus": ["Africa", "South Africa", "Egypt", "Morocco", "Tunisia", "Asia", "Latin America"],
            "cop31_antalya_role": "Co-launched '10by30' ($10B emerging market climate finance alliance) at COP31 on Nov 13 via Norwegian Climate Investment Fund",
            "cop31_verified_2026_commitment": "Co-anchoring $10B '10by30' by 2030 (63% Africa portfolio; priority markets South Africa, Egypt, Tunisia, Morocco, India, SE Asia)",
            "financing_instruments": ["Equity", "Mezzanine", "Long-Term Debt", "Co-Investment (10by30)", "Blended Finance"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 100_000_000,
            "target_sectors": ["Renewable Energy", "Energy Storage", "Electrification & Grid", "Industrial Decarbonization", "Sustainable Fuels"],
            "eligible_applicant_types": ["Project SPV", "Large Corporate", "Financial Intermediary", "Growth-Stage Private Enterprise"],
            "application_portal_url": "https://www.norfund.no/apply-for-funding/",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "High avoided-emissions potential replacing fossil-fuel power",
                "10by30 coordinated due diligence & IFC Performance Standards",
                "Norfund priority emerging markets (high-emitting developing countries)",
                "Clear additionality & private capital mobilization",
            ],
            "exclusion_rules": ["Fossil-fuel power plants", "Coal mining"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG enforces Norfund's strict priority-country and avoided-fossil-power criteria while RAG crafts 10by30 shared-pipeline teasers.",
            "verification_source_url": "https://www.byteseu.com/2521383/",
        },
        {
            "investor_id": "inv_findev_canada",
            "name": "FinDev Canada",
            "short_name": "FinDev Canada",
            "category": InvestorCategory.BILATERAL_DFI,
            "hq_country": "Canada",
            "geographic_focus": ["Africa", "Asia-Pacific", "Latin America", "Caribbean"],
            "cop31_antalya_role": "Co-launched '10by30' ($10B emerging market climate finance collaboration) at COP31 on Nov 13",
            "cop31_verified_2026_commitment": "Co-delivering $10B '10by30' via Climate Mobilization Strategy ($2.72B committed portfolio as of June 2026; 47% climate finance)",
            "financing_instruments": ["Senior/Subordinated Debt", "Equity", "Blended Finance", "Guarantee", "Technical Assistance"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 100_000_000,
            "target_sectors": ["Renewable Energy", "Energy Storage", "Electrification & Grid", "Clean Transport", "Sustainable Agriculture & Water", "Industrial Decarbonization"],
            "eligible_applicant_types": ["Project SPV", "Large Corporate", "Financial Intermediary", "Growth-Stage Private Enterprise"],
            "application_portal_url": "https://www.findevcanada.ca/en/what-we-do/how-we-invest",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "2X Challenge gender-lens & market development impact",
                "10by30 harmonized GHG & climate impact reporting",
                "IFC Performance Standards & E&S management system",
                "Geographic mandate (Africa, Asia-Pacific, LAC)",
            ],
            "exclusion_rules": ["Coal, upstream oil & gas, non-mandate high-income countries"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG enforces mandate geography, ticket sizing & 2X/ESG rules while RAG generates blended-finance & technical-assistance narratives.",
            "verification_source_url": "https://africa.businessinsider.com/local/markets/britain-canada-and-norway-combine-forces-for-dollar10-billion-climate-push-as-their/98mpx59",
        },
        {
            "investor_id": "inv_tskb",
            "name": "TSKB (Industrial Development Bank of Türkiye)",
            "short_name": "TSKB",
            "category": InvestorCategory.NATIONAL_DEV_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye", "EMEA"],
            "cop31_antalya_role": "Official COP31 Climate Supporter (Green Zone Block C Climate Finance Hub); Türkiye's sole IDFC member",
            "cop31_verified_2026_commitment": "€200M Treasury-guaranteed wind, solar & battery storage (BESS) facility + IDFC Climate Implementation Bridge & green corporate investment loans",
            "financing_instruments": ["Long-Term Investment Loan", "MDB On-Lending Credit Line", "Green/Sustainability Bond", "Apex SME Facility", "Advisory"],
            "typical_ticket_min_usd": 2_000_000,
            "typical_ticket_max_usd": 100_000_000,
            "target_sectors": ["Renewable Energy", "Energy Storage", "Industrial Decarbonization", "Energy Efficiency", "Circular Economy", "Women Empowerment & Inclusive Green"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "SME", "Mid-Cap Enterprise", "Financial Intermediary"],
            "application_portal_url": "https://www.tskb.com.tr/en/corporate-banking/corporate-loans",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "TSKB ERET Environmental & Social Risk Evaluation rating",
                "Turkish EIA (ÇED) permit & renewable license (EPDK) where applicable",
                "Measurable energy efficiency / tCO2e abatement baseline",
                "Audited corporate financials & debt service coverage (DSCR)",
            ],
            "exclusion_rules": ["New coal-fired power plants", "Environmental non-compliance"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG evaluates TSKB's MDB on-lending rules, ERET risk & Turkish licensing constraints while RAG aligns narratives with IDFC & COP31 green industry priorities.",
            "verification_source_url": "https://www.linkedin.com/in/meralmurathan/",
        },
        {
            "investor_id": "inv_turk_eximbank",
            "name": "Turk Eximbank",
            "short_name": "Turk Eximbank",
            "category": InvestorCategory.NATIONAL_DEV_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye", "Global Exports"],
            "cop31_antalya_role": "Signed 4 international green financing agreements >$800M at COP31 Antalya (IBRD, KfW, AIIB)",
            "cop31_verified_2026_commitment": ">$800M secured at COP31 (€209.2M IBRD, €250M KfW, $200M + $100M AIIB) dedicated to Turkish exporters' green transition & shock resilience",
            "financing_instruments": ["Green Export Investment Loan", "Export Working Capital Credit", "Export Credit Insurance", "MDB/DFI On-Lending Line"],
            "typical_ticket_min_usd": 500_000,
            "typical_ticket_max_usd": 75_000_000,
            "target_sectors": ["Industrial Decarbonization", "Renewable Energy", "Energy Efficiency", "SME Green Transition", "EU CBAM Export Compliance"],
            "eligible_applicant_types": ["Large Corporate", "SME", "Mid-Cap Enterprise"],
            "application_portal_url": "https://www.eximbank.gov.tr/en",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "Verified Turkish exporter status & export commitment",
                "Eligible green transition / CBAM decarbonization investment scope",
                "IBRD / KfW / AIIB on-lending Environmental & Social screening",
                "Bank letter of guarantee or eligible collateral",
            ],
            "exclusion_rules": ["Non-exporting domestic entities", "Coal/fossil-fuel expansion"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG enforces exporter/CBAM eligibility and MDB sub-loan rules while RAG tailors investment rationales to the new IBRD/KfW/AIIB COP31 lines.",
            "verification_source_url": "https://ua.news/en/dovkolo-svitu/turk-eximbank-zaluchiv-ponad-800-mln-na-cop31-u-turechchini-anadolu-agency",
        },
        {
            "investor_id": "inv_ilbank",
            "name": "İLBANK (İller Bankası — Türkiye Municipal Development Bank)",
            "short_name": "İLBANK",
            "category": InvestorCategory.NATIONAL_DEV_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye"],
            "cop31_antalya_role": "Signed municipal climate finance advisory agreement with EIB & City Climate Finance Gap Fund on Nov 13 at COP31",
            "cop31_verified_2026_commitment": "EIB & City Climate Finance Gap Fund advisory partnership for low-carbon, climate-resilient municipal urban infrastructure across Türkiye",
            "financing_instruments": ["Municipal Infrastructure Loan", "MDB On-Lending Credit", "Technical Assistance (Gap Fund)", "Resilient Urban Grant Co-Financing"],
            "typical_ticket_min_usd": 1_000_000,
            "typical_ticket_max_usd": 150_000_000,
            "target_sectors": ["Resilient Cities & Infrastructure", "Water & Wastewater Management", "Urban Mobility & Transport", "Renewable Energy", "Zero Waste & Circular Economy"],
            "eligible_applicant_types": ["Municipality", "Sovereign/Government", "Municipal Utility"],
            "application_portal_url": "https://www.ilbank.gov.tr/",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "Turkish municipality or municipal utility applicant status",
                "Municipal council borrowing resolution & Treasury debt limit compliance",
                "EIB / City Climate Finance Gap Fund climate resilience appraisal",
                "Environmental Impact Assessment (ÇED) & feasibility study",
            ],
            "exclusion_rules": ["Private non-municipal commercial projects", "Fossil-fuel infrastructure"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG strictly validates municipal legal eligibility & Treasury borrowing rules while RAG drafts EIB Gap Fund climate-resilience narratives.",
            "verification_source_url": "https://news.europawire.eu/eib-and-ilbank-launch-advisory-partnership-to-advance-climate-resilient-urban-investment-in-turkiye/eu-press-release/2026/11/13/17/05/05/187788/",
        },
        {
            "investor_id": "inv_bndes",
            "name": "BNDES (Brazilian Development Bank)",
            "short_name": "BNDES",
            "category": InvestorCategory.NATIONAL_DEV_BANK,
            "hq_country": "Brazil",
            "geographic_focus": ["Brazil", "Latin America"],
            "cop31_antalya_role": "Announced $300M GCF mobilization + $147M IBRD/CIF forest restoration + $1B IDB/IBRD industrial decarbonization LOI at COP31",
            "cop31_verified_2026_commitment": "R$39B ($6.9B) climate investment push anchored by $300M GCF (Flying Rivers Capital, Just Climate Brasil) + $147M IBRD/CIF forest restoration",
            "financing_instruments": ["Development Loan", "Climate Fund Equity Anchor", "Blended Concessional Finance", "Green Credit Line"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 300_000_000,
            "target_sectors": ["Nature-Based Solutions & Forestry", "Industrial Decarbonization", "Renewable Energy", "Sustainable Fuels", "Bioeconomy"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Fund Manager", "Municipality"],
            "application_portal_url": "https://www.bndes.gov.br/",
            "form_template_type": FormTemplateType.DFI_PROJECT_INTAKE,
            "mandatory_form_requirements": [
                "Brazilian operating entity / Climate Call alignment",
                "GCF / IBRD / CIF environmental & forest-protection safeguards",
                "Verified carbon abatement or reforestation hectares",
                "Brazilian regulatory & environmental licensing",
            ],
            "exclusion_rules": ["Illegal deforestation", "Coal power"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG enforces Brazilian jurisdiction & co-financier safeguards while RAG synthesizes Climate Call & nature-based fund theses.",
            "verification_source_url": "https://carbon-pulse.com/571307/",
        },

        # =====================================================================
        # CATEGORY 3: MULTILATERAL CLIMATE FUNDS — 5 Institutions
        # =====================================================================
        {
            "investor_id": "inv_gcf",
            "name": "Green Climate Fund (GCF)",
            "short_name": "GCF",
            "category": InvestorCategory.CLIMATE_FUND,
            "hq_country": "South Korea (UNFCCC Operating Entity)",
            "geographic_focus": ["Developing Countries", "Emerging Markets", "Global", "Africa", "Asia", "Latin America", "Türkiye"],
            "cop31_antalya_role": "Co-host of 2026 Climate Funds Pavilion (Blue Zone B2, D230); launched Adaptation Scaling-Up Framework with AF; $300M BNDES approval",
            "cop31_verified_2026_commitment": "$300M approved for Brazil climate funds at COP31 + new GCF-AF Adaptation Scaling-Up Framework + GFANZ Catalytic Capital Repository member",
            "financing_instruments": ["Grant", "Concessional Loan", "Equity", "Guarantee", "Results-Based Payment", "Blended Finance"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 250_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Renewable Energy", "Industrial Decarbonization", "Nature-Based Solutions & Forestry", "Sustainable Agriculture & Water", "Resilient Cities & Infrastructure"],
            "eligible_applicant_types": ["Accredited Entity/NGO", "Sovereign/Government", "Financial Intermediary", "Large Corporate", "Project SPV"],
            "application_portal_url": "https://www.greenclimate.fund/projects/process",
            "form_template_type": FormTemplateType.CLIMATE_FUND_PROPOSAL,
            "mandatory_form_requirements": [
                "Submission through a GCF Accredited Entity (AE) or Direct Access Entity (DAE)",
                "National Designated Authority (NDA) No-Objection Letter",
                "GCF 6 Investment Criteria (Impact, Paradigm Shift, Sustainable Development, Needs, Country Ownership, Efficiency)",
                "Gender Action Plan & Environmental/Social Management Plan (ESMP)",
            ],
            "exclusion_rules": ["Non-UNFCCC developing-country projects without NDA", "Coal or unabated fossil-fuel investments"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Mandatory multi-hop GCF rules (Applicant -> Accredited Entity -> NDA No-Objection -> 6 Investment Criteria -> Concessionality) demand strict KAG reasoning.",
            "verification_source_url": "https://www.climatechangenews.com/2026/11/10/cop31-bulletin-day-2-energy-day-off-to-slow-start-amid-transport-chaos/",
        },
        {
            "investor_id": "inv_cif",
            "name": "Climate Investment Funds (CIF / Clean Technology Fund)",
            "short_name": "CIF / CTF",
            "category": InvestorCategory.CLIMATE_FUND,
            "hq_country": "United States (Multilateral)",
            "geographic_focus": ["Developing Countries", "Emerging Markets", "Türkiye", "Africa", "Asia", "Latin America"],
            "cop31_antalya_role": "Co-host of Climate Funds Pavilion; launched $94M AMPLIFi clean electrification finance; seeded $250M CTF into Türkiye TIDIP",
            "cop31_verified_2026_commitment": "$94M AMPLIFi catalytic finance (mobilizing $1.2B+) + $250M CTF seed for Türkiye $6B TIDIP + $47M Brazil forest restoration",
            "financing_instruments": ["Catalytic Concessional Loan", "First-Loss Guarantee", "Grant", "Blended Finance (via MDBs)"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 250_000_000,
            "target_sectors": ["Electrification & Grid", "Industrial Decarbonization", "Renewable Energy", "Energy Storage", "Nature-Based Solutions & Forestry", "Coal Transition"],
            "eligible_applicant_types": ["Sovereign/Government", "Large Corporate", "Project SPV", "Financial Intermediary"],
            "application_portal_url": "https://www.cif.org/",
            "form_template_type": FormTemplateType.CLIMATE_FUND_PROPOSAL,
            "mandatory_form_requirements": [
                "Channeling through an implementing MDB (World Bank, IFC, EBRD, ADB, AfDB, IDB)",
                "Country Investment Plan endorsement (e.g., TIDIP / AMPLIFi / ACT)",
                "High private-sector capital mobilization ratio (typically >5x)",
                "Verified GHG abatement & transformational impact metrics",
            ],
            "exclusion_rules": ["Direct non-MDB applications", "Coal expansion"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG validates implementing-MDB & Country Investment Plan pathways while RAG crafts catalytic leverage and AMPLIFi/TIDIP transformation narratives.",
            "verification_source_url": "https://www.downtoearth.org.in/climate-change/cop31-starts-a-new-era-of-electrification",
        },
        {
            "investor_id": "inv_gef",
            "name": "Global Environment Facility (GEF — incl. LDCF & SCCF)",
            "short_name": "GEF",
            "category": InvestorCategory.CLIMATE_FUND,
            "hq_country": "United States (UNFCCC Operating Entity)",
            "geographic_focus": ["Developing Countries", "LDCs", "Emerging Markets", "Global", "Türkiye", "Africa", "Asia", "Latin America"],
            "cop31_antalya_role": "Co-host of 2026 Climate Funds Pavilion (Blue Zone B2, D230); hosting COP31 special events on LDCF, SCCF & GEF-9 priorities",
            "cop31_verified_2026_commitment": "Mobilizing LDCF, SCCF & GEF-9 adaptation, biodiversity, and climate innovation grants at COP31 Antalya",
            "financing_instruments": ["Grant", "Non-Grant Blended Instrument (NGI)", "Concessional Co-Financing", "Technical Assistance Grant"],
            "typical_ticket_min_usd": 500_000,
            "typical_ticket_max_usd": 30_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Biodiversity & Nature", "Circular Economy & Zero Waste", "Renewable Energy", "Sustainable Agriculture & Water", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Accredited Entity/NGO", "Sovereign/Government", "Municipality", "Climate-Tech Startup", "Financial Intermediary"],
            "application_portal_url": "https://www.thegef.org/projects-operations/how-apply",
            "form_template_type": FormTemplateType.CLIMATE_FUND_PROPOSAL,
            "mandatory_form_requirements": [
                "Endorsement Letter from host country's GEF Operational Focal Point (OFP)",
                "Implementation via one of 18 accredited GEF Agencies (UNDP, UNEP, World Bank, EBRD, ADB, AfDB, etc.)",
                "Global Environmental Benefits (GEB) & co-financing ratio verification",
                "GEF-9 / LDCF / SCCF alignment & Gender/Safeguards policy",
            ],
            "exclusion_rules": ["Unendorsed proposals lacking OFP letter", "Fossil-fuel subsidies"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Complex GEF Agency routing, OFP endorsement rules, and LDCF vs. SCCF vs. NGI window logic require deterministic KAG graph checks.",
            "verification_source_url": "https://www.thegef.org/events/gef-unfccc-cop31",
        },
        {
            "investor_id": "inv_adaptation_fund",
            "name": "Adaptation Fund (AF)",
            "short_name": "Adaptation Fund",
            "category": InvestorCategory.CLIMATE_FUND,
            "hq_country": "United States (UNFCCC / Paris Agreement Fund)",
            "geographic_focus": ["Developing Countries", "Vulnerable Countries", "Africa", "Asia", "Latin America", "Small Island Developing States"],
            "cop31_antalya_role": "Co-host of Climate Funds Pavilion; launched new Adaptation Scaling-Up Framework with GCF at COP31",
            "cop31_verified_2026_commitment": "Direct-access concrete adaptation grants + GCF-AF Scaling-Up Framework enabling proven AF projects to scale into larger GCF investments",
            "financing_instruments": ["Full Grant", "Small Innovation Grant", "Direct Access Grant", "Scaling-Up Pipeline to GCF"],
            "typical_ticket_min_usd": 250_000,
            "typical_ticket_max_usd": 20_000_000,
            "target_sectors": ["Climate Adaptation & Resilience", "Sustainable Agriculture & Water", "Coastal & Flood Resilience", "Early Warning Systems", "Community Resilience"],
            "eligible_applicant_types": ["Accredited Entity/NGO", "Sovereign/Government", "Municipality"],
            "application_portal_url": "https://www.adaptation-fund.org/apply-funding/",
            "form_template_type": FormTemplateType.CLIMATE_FUND_PROPOSAL,
            "mandatory_form_requirements": [
                "Submission via National Implementing Entity (NIE), Regional (RIE), or Multilateral (MIE)",
                "Designated Authority (DA) Endorsement Letter",
                "Concrete, localized climate adaptation outcomes (100% grant eligible)",
                "Adaptation Fund Environmental, Social & Gender Policies",
            ],
            "exclusion_rules": ["Pure mitigation projects without concrete adaptation benefits", "Developed-country applicants"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Strict NIE/RIE/MIE accreditation, Designated Authority endorsement, and country cap constraints require KAG logical verification.",
            "verification_source_url": "https://www.climatechangenews.com/2026/11/10/cop31-bulletin-day-2-energy-day-off-to-slow-start-amid-transport-chaos/",
        },
        {
            "investor_id": "inv_frld",
            "name": "Fund for Responding to Loss and Damage (FRLD)",
            "short_name": "Loss & Damage Fund",
            "category": InvestorCategory.CLIMATE_FUND,
            "hq_country": "Philippines (Host) / UNFCCC",
            "geographic_focus": ["Developing Countries", "Vulnerable Countries", "LDCs", "SIDS", "Asia", "Africa", "Latin America"],
            "cop31_antalya_role": "Co-host of Climate Funds Pavilion; marked first operational delivery allocation ($21.6M for Nepal) highlighted at COP31",
            "cop31_verified_2026_commitment": "First provisional recovery allocation ($21.6M for Nepal post-flood recovery) signaling operational rollout of Loss & Damage grants at COP31",
            "financing_instruments": ["Rapid-Response Recovery Grant", "Non-Debt Concessional Recovery Support", "Budget Support"],
            "typical_ticket_min_usd": 1_000_000,
            "typical_ticket_max_usd": 50_000_000,
            "target_sectors": ["Climate Disaster Recovery", "Climate Adaptation & Resilience", "Resilient Reconstruction", "Early Recovery Infrastructure"],
            "eligible_applicant_types": ["Sovereign/Government", "Accredited Entity/NGO"],
            "application_portal_url": "https://www.frld.org/",
            "form_template_type": FormTemplateType.CLIMATE_FUND_PROPOSAL,
            "mandatory_form_requirements": [
                "Particularly vulnerable developing country sovereign request",
                "Verified climate-induced extreme weather or slow-onset loss & damage assessment",
                "National Focal Point / Ministry of Finance endorsement",
                "Fiduciary transparency & rapid disbursement safeguards",
            ],
            "exclusion_rules": ["Commercial private-sector profit ventures", "Non-climate-disaster projects"],
            "recommended_ai_model_type": AIModelArchitecture.KAG,
            "ai_model_rationale": "Strict vulnerability eligibility, sovereign-request validation, and disaster-attribution compliance rules require deterministic KAG gating.",
            "verification_source_url": "https://indiasworld.in/cop31-in-antalya-key-issues-and-challenges/",
        },

        # =====================================================================
        # CATEGORY 4: TURKISH & GLOBAL COMMERCIAL / STATE BANKS — 12 Institutions
        # =====================================================================
        {
            "investor_id": "inv_bbva_group",
            "name": "BBVA Group",
            "short_name": "BBVA",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "hq_country": "Spain",
            "geographic_focus": ["Global", "Europe", "Türkiye", "Latin America", "North America", "Emerging Markets"],
            "cop31_antalya_role": "Official Global Banking Partner of COP31 Antalya; 400m² Green Zone Pavilion with 60+ climate finance sessions",
            "cop31_verified_2026_commitment": "€700B sustainable business goal (2025–2029; €170B mobilized by Q1 2026; €36B in Q1 2026 alone) across electrification, cleantech & transition",
            "financing_instruments": ["Green Loan", "Sustainability-Linked Loan (SLL)", "Green Bond Underwriting", "Project Finance", "Cleantech Venture Debt"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 500_000_000,
            "target_sectors": ["Electrification & Grid", "Renewable Energy", "Climate-Tech Innovation", "Industrial Decarbonization", "Climate Adaptation & Resilience", "Nature & Water"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Climate-Tech Startup", "Mid-Cap Enterprise", "Financial Intermediary"],
            "application_portal_url": "https://www.bbva.com/en/sustainability/",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "LMA Green Loan Principles / Sustainability-Linked Loan Principles / ICMA GBP alignment",
                "EU Taxonomy or BBVA Sustainable Finance Framework eligibility",
                "Scope 1/2/3 decarbonization KPIs & transition plan",
                "Credit underwriting & Second-Party Opinion (for labeled bonds/SLLs)",
            ],
            "exclusion_rules": ["Thermal coal expansion", "Unaligned high-controversy projects"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "BBVA's 6 COP31 focus areas, extensive sustainable finance catalog, and narrative taxonomy/SPT alignment are ideally served by high-precision RAG retrieval.",
            "verification_source_url": "https://www.bbva.com/en/sustainability/bbva-to-be-the-global-banking-partner-of-the-united-nations-climate-summit-cop31-in-turkiye/",
        },
        {
            "investor_id": "inv_garanti_bbva",
            "name": "Garanti BBVA",
            "short_name": "Garanti BBVA",
            "category": InvestorCategory.TURKISH_COMMERCIAL_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye", "EMEA"],
            "cop31_antalya_role": "Official Global Banking Partner of COP31 Antalya (with BBVA Group); 60+ Green Zone Climate Finance Hub sessions; EV/TOGG mobility showcase",
            "cop31_verified_2026_commitment": "TRY 3.5 trillion sustainable finance commitment (2018–2029; >TRY 1 trillion surpassed by Jan 2026) for green transition, renewables, e-mobility & SMEs",
            "financing_instruments": ["Green Investment Loan", "Sustainability-Linked Loan", "SME Green Transformation Loan", "EV/E-Mobility Finance", "Green Trade Finance"],
            "typical_ticket_min_usd": 100_000,
            "typical_ticket_max_usd": 150_000_000,
            "target_sectors": ["Renewable Energy", "Clean Transport & EV", "Industrial Decarbonization", "SME Green Transition", "Water Management & Circular Economy", "Green Buildings"],
            "eligible_applicant_types": ["Large Corporate", "SME", "Mid-Cap Enterprise", "Project SPV", "Climate-Tech Startup"],
            "application_portal_url": "https://www.garantibbva.com.tr/en/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish company registration (VKN) & audited financials",
                "Garanti BBVA Sustainable Finance Framework eligibility",
                "Environmental permits (ÇED/EIA) & energy/carbon savings verification",
                "Collateral / creditworthiness or KGF guarantee package",
            ],
            "exclusion_rules": ["New thermal coal projects", "Environmental regulation breaches"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "Rich catalog of Turkish corporate/SME green products, EV mobility packages, and sustainability framework docs fit RAG retrieval directly.",
            "verification_source_url": "https://www.garantibbva.com.tr/en/corporate-communications/cop31-climate-change-summit",
        },
        {
            "investor_id": "inv_isbank",
            "name": "Türkiye İş Bankası (İşbank)",
            "short_name": "İşbank",
            "category": InvestorCategory.TURKISH_COMMERCIAL_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye", "EMEA"],
            "cop31_antalya_role": "Official COP31 Climate Supporter at Climate Finance Hub; showcasing energy transition, green industrialization & marine conservation models",
            "cop31_verified_2026_commitment": "COP31 Climate Finance Hub green transformation, SME packages, energy transition, sustainable tourism & blue economy financing models",
            "financing_instruments": ["Green Investment Loan", "SME Eco-Efficiency Loan", "Blue Economy / Sustainable Tourism Loan", "Project Finance", "Green Trade Credit"],
            "typical_ticket_min_usd": 100_000,
            "typical_ticket_max_usd": 150_000_000,
            "target_sectors": ["Renewable Energy", "Industrial Decarbonization", "Blue Economy & Marine Conservation", "Sustainable Tourism", "SME Green Transition", "Energy Efficiency"],
            "eligible_applicant_types": ["Large Corporate", "SME", "Mid-Cap Enterprise", "Project SPV", "Climate-Tech Startup"],
            "application_portal_url": "https://www.isbank.com.tr/en/about-us/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish legal entity (VKN) & credit bureau clearance",
                "Eligible green transition, renewable, or blue-economy use of proceeds",
                "Environmental permits (ÇED/EIA) & supplier green equipment specs",
                "Collateral / KGF guarantee verification",
            ],
            "exclusion_rules": ["Unabated coal power", "Marine ecosystem degradation"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "Diverse sector packages (energy, green industry, tourism, marine conservation) are best retrieved and tailored via RAG over İşbank's product corpus.",
            "verification_source_url": "https://www.bolgegundemi.com/antalya/bankalar-cop31-kapsaminda-iklim-finansmani-modellerini-tanitacak-229994.html",
        },
        {
            "investor_id": "inv_akbank",
            "name": "Akbank",
            "short_name": "Akbank",
            "category": InvestorCategory.TURKISH_COMMERCIAL_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye"],
            "cop31_antalya_role": "Active COP31 Green Zone exhibitor partnering with GEFF Türkiye, KGF, Migros & TARİŞ on sustainable agriculture, circular industry & women's green access",
            "cop31_verified_2026_commitment": "TRY 2.5 trillion sustainable finance target through 2030; COP31 programs spanning GEFF Türkiye, KGF-backed sustainable agri & circular industrial loans",
            "financing_instruments": ["GEFF Türkiye Green Loan", "KGF-Backed Sustainability Loan", "Corporate Transition Loan", "Sustainable Agriculture Credit", "Green Leasing"],
            "typical_ticket_min_usd": 50_000,
            "typical_ticket_max_usd": 120_000_000,
            "target_sectors": ["SME Green Transition", "Sustainable Agriculture & Water", "Circular Economy & Zero Waste", "Renewable Energy", "Industrial Decarbonization", "Women-Led Green Enterprise"],
            "eligible_applicant_types": ["SME", "Large Corporate", "Mid-Cap Enterprise", "Project SPV", "Climate-Tech Startup"],
            "application_portal_url": "https://www.akbank.com/en-us/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish VKN registration & credit eligibility",
                "GEFF Türkiye Technology Selector or Akbank Sustainable Finance Framework match",
                "KGF eligibility check (for KGF-backed SME green lines)",
                "Carbon/water savings estimate & environmental compliance",
            ],
            "exclusion_rules": ["Thermal coal mining/generation", "Non-compliant industrial waste"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG accurately matches applicants across Akbank's GEFF Türkiye, KGF agri, circular economy, and women-led green transition product guidelines.",
            "verification_source_url": "https://basakgazetesi.com/haber/akbank-cop31-icin-kapsamli-iklim-finansmani-ve-donusum-programini-acikladi-897587",
        },
        {
            "investor_id": "inv_ziraat_bankasi",
            "name": "Ziraat Bankası",
            "short_name": "Ziraat Bankası",
            "category": InvestorCategory.TURKISH_STATE_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye"],
            "cop31_antalya_role": "Official COP31 Main Partner (Culture & Civilization Partner); COP31 panel on green SME, CBAM exporter & climate-smart agricultural financing",
            "cop31_verified_2026_commitment": "$2.9B sustainability-linked syndicated financing in 2026 + $2B additional planned during COP31; Carbon Border Reduction Package (20% emission cut) & Green Export Loan",
            "financing_instruments": ["Carbon Border (CBAM) Reduction Loan", "Green Export Loan (SME)", "Organized Industrial Zone (OIZ) Green Package", "Climate-Smart Agricultural Loan"],
            "typical_ticket_min_usd": 50_000,
            "typical_ticket_max_usd": 100_000_000,
            "target_sectors": ["Sustainable Agriculture & Water", "EU CBAM Export Compliance", "Industrial Decarbonization", "SME Green Transition", "Renewable Energy"],
            "eligible_applicant_types": ["SME", "Large Corporate", "Mid-Cap Enterprise", "Agricultural Cooperative"],
            "application_portal_url": "https://www.ziraatbank.com.tr/en/our-bank/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish enterprise / farmer / OIZ registration (VKN/ÇKS)",
                "Target >=20% carbon footprint reduction (for Carbon Border Reduction Package)",
                "Export documentation (for Green Export Loan) or agricultural certification",
                "Collateral or KGF guarantee package",
            ],
            "exclusion_rules": ["Environmentally prohibited activities", "Unpermitted water extraction"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG maps diverse Turkish exporter, OIZ, and agricultural SME profiles to Ziraat's specific CBAM, Green Export, and organic farming credit packages.",
            "verification_source_url": "https://www.dailysabah.com/business/energy/turkish-state-banks-expand-green-financing-for-smes-at-cop31",
        },
        {
            "investor_id": "inv_halkbank",
            "name": "Halkbank",
            "short_name": "Halkbank",
            "category": InvestorCategory.TURKISH_STATE_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye"],
            "cop31_antalya_role": "Official COP31 Main Partner; launched dedicated COP31 TRY 100B SME Sustainability Transformation Package (31 products)",
            "cop31_verified_2026_commitment": "TRY 100 billion COP31 SME Sustainability Transformation Package (31 green/social credit products, partly KGF-backed; TRY 424B cumulative green/social contribution)",
            "financing_instruments": ["SME Sustainability Transformation Loan (31 products)", "KGF-Backed Green Loan", "EV Charging & Solar Loan", "Women & Youth Entrepreneur Green Credit"],
            "typical_ticket_min_usd": 25_000,
            "typical_ticket_max_usd": 50_000_000,
            "target_sectors": ["SME Green Transition", "Renewable Energy", "Energy Efficiency", "Circular Economy & Zero Waste", "Clean Transport & EV", "Water Conservation"],
            "eligible_applicant_types": ["SME", "Mid-Cap Enterprise", "Women/Youth Entrepreneur", "Large Corporate"],
            "application_portal_url": "https://www.halkbank.com.tr/en/sustainability.html",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish SME / tradesperson / corporate registration (VKN & KOSGEB/KOBİ status)",
                "Selection among 31 eligible green/social transformation credit categories",
                "KGF guarantee or collateral documentation",
                "Environmental permit & vendor invoice/proforma for green equipment",
            ],
            "exclusion_rules": ["Non-eligible speculative lending", "High-pollution non-compliant operations"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "Choosing the optimal match across Halkbank's 31 COP31 SME green loan sub-products is a textbook semantic RAG retrieval task.",
            "verification_source_url": "https://www.cnbce.com/haberler/halkbank-cop31-icin-hazirladi-kobilere-100-milyar-tl-finansman-h41356",
        },
        {
            "investor_id": "inv_vakifbank",
            "name": "VakıfBank",
            "short_name": "VakıfBank",
            "category": InvestorCategory.TURKISH_STATE_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye"],
            "cop31_antalya_role": "Official COP31 Main Partner; channeling $500M ADB green/inclusive SME financing agreement signed at COP31",
            "cop31_verified_2026_commitment": "$500M ADB long-term financing facility signed at COP31 for SMEs in less-developed & earthquake-affected provinces plus women entrepreneurs",
            "financing_instruments": ["ADB-Backed Green SME Loan", "Sustainable Transition Loan", "Women Entrepreneur Green Facility", "Green Bond Proceeds Loan"],
            "typical_ticket_min_usd": 50_000,
            "typical_ticket_max_usd": 75_000_000,
            "target_sectors": ["SME Green Transition", "Climate Adaptation & Resilience", "Renewable Energy", "Energy Efficiency", "Women-Led Green Enterprise"],
            "eligible_applicant_types": ["SME", "Mid-Cap Enterprise", "Large Corporate", "Women/Youth Entrepreneur"],
            "application_portal_url": "https://www.vakifbank.com.tr/en/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish SME/corporate registration (VKN)",
                "ADB sub-loan E&S screening & inclusive priority verification (region / women ownership)",
                "Green investment purpose & energy/resilience benefit statement",
                "Financial statements & collateral/KGF guarantee",
            ],
            "exclusion_rules": ["ADB Safeguards Prohibited Investment Activities List"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG validates ADB sub-loan inclusive/regional priority rules while RAG populates VakıfBank's green SME credit narrative.",
            "verification_source_url": "https://www.trtworld.com/article/08c7af154347",
        },
        {
            "investor_id": "inv_yapi_kredi",
            "name": "Yapı Kredi",
            "short_name": "Yapı Kredi",
            "category": InvestorCategory.TURKISH_COMMERCIAL_BANK,
            "hq_country": "Türkiye",
            "geographic_focus": ["Türkiye"],
            "cop31_antalya_role": "Launched 'Yapı Kredi Dönüşüme Tam Destek Programı' (6-category green & digital SME transformation program) at COP31",
            "cop31_verified_2026_commitment": "COP31 'Dönüşüme Tam Destek' 6-category green/digital SME loan program + 20% Eco Foreign Trade discount + free carbon footprint & water efficiency platforms",
            "financing_instruments": ["Dönüşüme Tam Destek Green Loan", "Eco Foreign Trade Finance Package", "Solar/Energy Efficiency Loan", "Green Digital Transformation Credit"],
            "typical_ticket_min_usd": 50_000,
            "typical_ticket_max_usd": 100_000_000,
            "target_sectors": ["SME Green Transition", "Renewable Energy", "Water Management & Efficiency", "Industrial Decarbonization", "Digital & Green Twin Transition"],
            "eligible_applicant_types": ["SME", "Mid-Cap Enterprise", "Large Corporate"],
            "application_portal_url": "https://www.yapikredi.com.tr/en/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish company registration (VKN) & credit history",
                "Alignment with 1 of 6 Dönüşüme Tam Destek green/digital categories",
                "Baseline carbon footprint or water-efficiency calculation",
                "Collateral / credit line limit approval",
            ],
            "exclusion_rules": ["Coal expansion", "Unpermitted hazardous waste operations"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG retrieves exact eligibility and benefit bundles across Yapı Kredi's 6 COP31 transformation categories and eco foreign-trade tools.",
            "verification_source_url": "https://www.fintechdunyasi.com/cop31de-bankalardan-iklim-finansmani-hamlesi-yeni-finansman-anlasmalari-kobi-programlari-ve-surdurulebilirlik-mesajlari/28721/",
        },
        {
            "investor_id": "inv_qnb_turkiye",
            "name": "QNB Türkiye & QNB Leasing",
            "short_name": "QNB Türkiye",
            "category": InvestorCategory.TURKISH_COMMERCIAL_BANK,
            "hq_country": "Türkiye (Qatar National Bank Group)",
            "geographic_focus": ["Türkiye", "MENA"],
            "cop31_antalya_role": "Secured up to $500M sustainable finance at COP31 including €75M Proparco solar & wind leasing agreement",
            "cop31_verified_2026_commitment": "Up to $500M sustainable financing arrangements at COP31 + €75M Proparco renewable energy leasing (>€250M 2026 solar/wind leasing with Proparco)",
            "financing_instruments": ["Renewable Energy Equipment Leasing", "Green Investment Loan", "SME Energy Efficiency Finance", "Sustainable Trade Finance"],
            "typical_ticket_min_usd": 100_000,
            "typical_ticket_max_usd": 80_000_000,
            "target_sectors": ["Renewable Energy", "Solar & Wind Power Plants", "Energy Efficiency", "SME Green Transition", "Industrial Decarbonization"],
            "eligible_applicant_types": ["SME", "Mid-Cap Enterprise", "Large Corporate", "Project SPV"],
            "application_portal_url": "https://www.qnb.com.tr/en/sustainability",
            "form_template_type": FormTemplateType.TURKISH_BANK_GREEN_LOAN,
            "mandatory_form_requirements": [
                "Turkish company registration (VKN) & leasing/credit underwriting",
                "Proparco/DFI green equipment eligibility (solar PV, wind turbines, efficiency gear)",
                "EPDK connection/call letter for rooftop/utility solar or wind",
                "Equipment vendor quote & E&S compliance",
            ],
            "exclusion_rules": ["Fossil-fuel machinery", "Proparco Exclusion List activities"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG grounds green leasing & renewable equipment applications against QNB Türkiye and Proparco COP31 solar/wind eligibility guides.",
            "verification_source_url": "https://www.asigazetesi.com/iklim-zirvesi-cop31-antalya-qnb-leasing-ile-proparcodan-75-milyon-avroluk-surdurulebilir-enerji-anlasmasi",
        },
        {
            "investor_id": "inv_bnp_paribas",
            "name": "BNP Paribas",
            "short_name": "BNP Paribas",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "hq_country": "France",
            "geographic_focus": ["Global", "Europe", "EMEA", "Türkiye", "Americas", "Asia-Pacific"],
            "cop31_antalya_role": "Major international banking delegation at COP31 Antalya (22 accredited delegates) engaging in corporate transition & green bond dialogues",
            "cop31_verified_2026_commitment": "Global low-carbon energy transition financing, green bond structuring, and corporate sustainability-linked lending active at COP31",
            "financing_instruments": ["Green Bond Structuring", "Sustainability-Linked Loan (SLL)", "Renewable Project Finance", "Green Trade Finance", "Transition Advisory"],
            "typical_ticket_min_usd": 20_000_000,
            "typical_ticket_max_usd": 500_000_000,
            "target_sectors": ["Renewable Energy", "Electrification & Grid", "Industrial Decarbonization", "Clean Transport", "Green Buildings", "Energy Storage"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Sovereign/Government"],
            "application_portal_url": "https://cib.bnpparibas/sustainable-finance/",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "ICMA Green Bond Principles / LMA GLP or SLLP compliance",
                "Credible corporate net-zero transition plan & Scope 1/2/3 baselines",
                "Second-Party Opinion (SPO) & external KPI assurance",
                "Investment-grade or bankable project finance cash flows",
            ],
            "exclusion_rules": ["New oil & gas field financing", "Thermal coal mining/power"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG excels at grounding EU Taxonomy, ICMA/LMA SPT targets, and corporate transition narratives in BNP Paribas CIB's policy disclosures.",
            "verification_source_url": "https://thefederal.com/the-federal-special/cop31-in-antalya-big-polluters-and-climate-activists-under-one-roof-262803",
        },
        {
            "investor_id": "inv_hsbc",
            "name": "HSBC",
            "short_name": "HSBC",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "hq_country": "United Kingdom",
            "geographic_focus": ["Global", "Asia-Pacific", "Europe", "MENA", "Türkiye", "Americas"],
            "cop31_antalya_role": "Prominent international banking delegation at COP31 Antalya (19 accredited delegates) focused on transition finance & green supply chains",
            "cop31_verified_2026_commitment": "Global sustainable finance & investment mobilization ($750B–$1T 2030 target) across green trade, supply chain decarbonization & transition loans",
            "financing_instruments": ["Green Trade Finance", "Sustainability-Linked Loan (SLL)", "Green Bond Underwriting", "Transition Finance Facility", "Supply Chain Decarbonization Finance"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 500_000_000,
            "target_sectors": ["Industrial Decarbonization", "Renewable Energy", "Sustainable Supply Chains", "Climate-Tech Innovation", "Green Buildings", "Clean Transport"],
            "eligible_applicant_types": ["Large Corporate", "Mid-Cap Enterprise", "Project SPV", "Financial Intermediary"],
            "application_portal_url": "https://www.business.hsbc.com/en-gb/solutions/sustainable-finance",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "HSBC Sustainable Finance & Transition Framework alignment",
                "Measurable Scope 1/2/3 KPIs & LMA/APLMA GLP/SLLP structuring",
                "Second-Party Opinion (SPO) or third-party verification",
                "Corporate creditworthiness & ESG controversy screening",
            ],
            "exclusion_rules": ["New thermal coal power/mines", "New oil & gas fields"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG retrieves HSBC's green trade, supply-chain, and transition-loan framework criteria to draft bankable SPT and Use-of-Proceeds entries.",
            "verification_source_url": "https://thefederal.com/the-federal-special/cop31-in-antalya-big-polluters-and-climate-activists-under-one-roof-262803",
        },
        {
            "investor_id": "inv_standard_chartered",
            "name": "Standard Chartered Bank",
            "short_name": "Standard Chartered",
            "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
            "hq_country": "United Kingdom",
            "geographic_focus": ["Emerging Markets", "Asia", "Africa", "MENA", "Türkiye", "Global"],
            "cop31_antalya_role": "Senior Sustainable Finance Advisory speakers at COP31 Antalya; emerging markets blended & transition finance",
            "cop31_verified_2026_commitment": "Emerging-market sustainable finance ($300B 2030 mobilization goal), blended adaptation finance, green trade & Article 6 carbon finance structuring",
            "financing_instruments": ["Green & Transition Loan", "Blended Finance Structuring", "Green Trade Finance", "Carbon Market Financing", "Sustainable Bond"],
            "typical_ticket_min_usd": 10_000_000,
            "typical_ticket_max_usd": 350_000_000,
            "target_sectors": ["Renewable Energy", "Climate Adaptation & Resilience", "Industrial Decarbonization", "Carbon Markets & Article 6", "Sustainable Trade & Supply Chains"],
            "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Sovereign/Government"],
            "application_portal_url": "https://www.sc.com/en/sustainability/sustainable-finance/",
            "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
            "mandatory_form_requirements": [
                "Standard Chartered Green & Sustainable Product Framework",
                "Transition Finance Framework & credible decarbonization pathway",
                "Emerging market ESG & Equator Principles screening",
                "Second-Party Opinion / external assurance for labeled instruments",
            ],
            "exclusion_rules": ["Unabated coal expansion", "Equator Principles breaches"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG captures Standard Chartered's specialized emerging-market adaptation, transition, and Article 6 carbon-finance guidelines.",
            "verification_source_url": "https://cop.sifiratikvakfi.org/en/speakers/",
        },

        # =====================================================================
        # CATEGORY 5: INSTITUTIONAL, CATALYTIC CAPITAL & CLIMATE PE — 5 Institutions
        # =====================================================================
        {
            "investor_id": "inv_gfanz_ccr",
            "name": "GFANZ / Catalytic Capital Repository (GCBC)",
            "short_name": "GFANZ Catalytic Capital",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "hq_country": "United Kingdom / Global Coalition",
            "geographic_focus": ["Emerging Markets", "Developing Countries", "Türkiye", "Africa", "Asia", "Latin America", "Global"],
            "cop31_antalya_role": "Launched 'Catalytic Capital Repository' (30+ financial institutions) at COP31 Nov 11–12; partnered with Türkiye Ministry of Industry & Technology on industrial decarbonization; co-hosted Global Finance Summit",
            "cop31_verified_2026_commitment": "Public repository of 30+ catalytic capital & risk-mitigation providers for EMDE clean energy/resilience + Türkiye industrial decarbonization private-capital partnership",
            "financing_instruments": ["Catalytic First-Loss Capital", "Risk-Mitigation Guarantee", "Blended Transition Facility", "Co-Investment Syndication"],
            "typical_ticket_min_usd": 5_000_000,
            "typical_ticket_max_usd": 200_000_000,
            "target_sectors": ["Industrial Decarbonization", "Renewable Energy", "Electrification & Grid", "Climate Adaptation & Resilience", "Energy Storage"],
            "eligible_applicant_types": ["Project SPV", "Large Corporate", "Financial Intermediary", "Fund Manager", "Climate-Tech Startup"],
            "application_portal_url": "https://www.gfanzero.com/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Clear private-capital mobilization & de-risking thesis (EMDEs)",
                "Alignment with GFANZ Transition Finance guidelines",
                "Defined blended capital stack showing catalytic layer role",
                "Quantified GHG avoidance or climate resilience impact",
            ],
            "exclusion_rules": ["Unabated coal expansion", "Non-catalytic purely commercial subsidies without additionality"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG maps multi-institution repository eligibility & blended capital stack rules while RAG drafts catalytic additionality and mobilization theses.",
            "verification_source_url": "https://www.esgdive.com/news/platform-launched-at-cop31-aims-to-scale-transition-capital-in-emerging-mar/874527/",
        },
        {
            "investor_id": "inv_allied_climate_partners",
            "name": "Allied Climate Partners (ACP)",
            "short_name": "Allied Climate Partners",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "hq_country": "United States (Philanthropic Catalytic Investor)",
            "geographic_focus": ["Emerging Markets", "Developing Countries", "Africa", "Asia", "Latin America", "Caribbean"],
            "cop31_antalya_role": "Founding cohort member of the GFANZ Catalytic Capital Repository launched at COP31 Antalya",
            "cop31_verified_2026_commitment": "Early-stage philanthropic catalytic equity & development capital unlocking bankable climate infrastructure pipelines in emerging markets",
            "financing_instruments": ["Early-Stage Development Equity", "Catalytic First-Loss Capital", "Project Preparation Funding", "Co-Development Platform"],
            "typical_ticket_min_usd": 1_000_000,
            "typical_ticket_max_usd": 25_000_000,
            "target_sectors": ["Renewable Energy", "Energy Storage", "Electrification & Grid", "Clean Transport", "Climate Adaptation & Resilience", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Project SPV", "Fund Manager", "Project Developer"],
            "application_portal_url": "https://www.alliedclimatepartners.org/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Early-stage / pre-FID bankability gap in emerging markets",
                "High downstream commercial capital mobilization potential",
                "Experienced local/regional project development team",
                "Clear measurable tCO2e abatement or resilience impact",
            ],
            "exclusion_rules": ["Fossil-fuel generation", "Developed-market-only deployments"],
            "recommended_ai_model_type": AIModelArchitecture.HYBRID_KAG_RAG,
            "ai_model_rationale": "KAG verifies early-stage emerging-market & ticket constraints while RAG crafts catalytic project-prep & bankability-unlocking narratives.",
            "verification_source_url": "https://www.esgdive.com/news/platform-launched-at-cop31-aims-to-scale-transition-capital-in-emerging-mar/874527/",
        },
        {
            "investor_id": "inv_just_climate",
            "name": "Just Climate (Generation Investment Management)",
            "short_name": "Just Climate",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "hq_country": "United Kingdom",
            "geographic_focus": ["Global", "Europe", "Latin America", "Brazil", "Emerging Markets", "North America"],
            "cop31_antalya_role": "Backed by R$870M BNDES anchor allocation announced at COP31 for Just Climate Brasil (targeting R$3.8B) + global industrial climate equity",
            "cop31_verified_2026_commitment": "Just Climate Brasil targeting R$3.8B (~$670M) backed by R$870M BNDES COP31 allocation + Industrial & Natural Climate Solutions equity strategies",
            "financing_instruments": ["Growth Private Equity", "Climate Infrastructure Equity", "Natural Climate Solutions Equity"],
            "typical_ticket_min_usd": 15_000_000,
            "typical_ticket_max_usd": 150_000_000,
            "target_sectors": ["Industrial Decarbonization", "Nature-Based Solutions & Forestry", "Sustainable Agriculture & Water", "Energy Storage", "Clean Transport", "Climate-Tech Innovation"],
            "eligible_applicant_types": ["Climate-Tech Startup", "Growth-Stage Private Enterprise", "Project SPV", "Large Corporate"],
            "application_portal_url": "https://www.justclimate.com/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Climate-led investing thesis targeting highest-emitting hard-to-abate or nature sectors",
                "Quantified GHG abatement potential per dollar invested (tCO2e/$)",
                "Commercial scale-up traction & risk-adjusted equity return profile",
                "Strong governance & impact verification methodology",
            ],
            "exclusion_rules": ["Unabated fossil fuels", "Deforestation-linked supply chains"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG tailors investment memos to Just Climate's climate-led abatement-per-dollar and hard-to-abate industrial/nature theses.",
            "verification_source_url": "https://carbon-pulse.com/571307/",
        },
        {
            "investor_id": "inv_blackrock_climate_infra",
            "name": "BlackRock (Climate Infrastructure & Transition Investing)",
            "short_name": "BlackRock Climate Infra",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "hq_country": "United States",
            "geographic_focus": ["Global", "Europe", "North America", "Asia-Pacific", "Emerging Markets", "Türkiye"],
            "cop31_antalya_role": "Active delegation at COP31 Antalya participating in energy transition infrastructure & private capital dialogues",
            "cop31_verified_2026_commitment": "Global Climate Infrastructure & Energy Transition institutional funds (including emerging markets blended Climate Finance Partnership)",
            "financing_instruments": ["Infrastructure Equity", "Blended Transition Equity (CFP)", "Project Equity", "Long-Term Infrastructure Debt"],
            "typical_ticket_min_usd": 25_000_000,
            "typical_ticket_max_usd": 500_000_000,
            "target_sectors": ["Renewable Energy", "Energy Storage", "Electrification & Grid", "Industrial Decarbonization", "Clean Transport", "Carbon Capture & Storage"],
            "eligible_applicant_types": ["Project SPV", "Large Corporate", "Growth-Stage Private Enterprise", "Infrastructure Developer"],
            "application_portal_url": "https://www.blackrock.com/institutions/en-us/capabilities/alternatives/infrastructure",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Contracted long-term cash flows (PPAs / offtake agreements)",
                "Institutional-scale capex & commercial IRR benchmarks",
                "Comprehensive technical, legal & ESG due diligence",
                "Proven management / EPC track record",
            ],
            "exclusion_rules": ["Unbankable early-R&D ventures without commercial path", "Thermal coal"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG matches infrastructure deal teasers against BlackRock's institutional transition-infrastructure underwriting and PPA criteria.",
            "verification_source_url": "https://www.theguardian.com/environment/2026/nov/13/cop31-companies-and-groups-linked-to-fossil-fuels-delegations",
        },
        {
            "investor_id": "inv_iigcc_bloomberg",
            "name": "IIGCC & Bloomberg Philanthropies Climate Finance Network",
            "short_name": "IIGCC / Bloomberg",
            "category": InvestorCategory.INSTITUTIONAL_CATALYTIC_PE,
            "hq_country": "United Kingdom / United States",
            "geographic_focus": ["Global", "Europe", "Türkiye", "Emerging Markets", "Developing Countries"],
            "cop31_antalya_role": "IIGCC is founding member of COP31 Electrify Now Finance Coalition; Bloomberg Philanthropies is official COP31 Action Agenda partner co-hosting Global Finance Summit",
            "cop31_verified_2026_commitment": "Mobilizing institutional asset owners & philanthropic catalytic grants across clean electrification, zero waste, methane abatement & industrial transition at COP31",
            "financing_instruments": ["Institutional Co-Investment Syndication", "Philanthropic Catalytic Grant", "Net-Zero Asset Owner Mandates", "Project Preparation Support"],
            "typical_ticket_min_usd": 1_000_000,
            "typical_ticket_max_usd": 200_000_000,
            "target_sectors": ["Electrification & Grid", "Renewable Energy", "Methane Abatement", "Zero Waste & Circular Economy", "Ocean-Climate Action", "Industrial Decarbonization"],
            "eligible_applicant_types": ["Project SPV", "Large Corporate", "Municipality", "Climate-Tech Startup", "Accredited Entity/NGO", "Fund Manager"],
            "application_portal_url": "https://www.iigcc.org/",
            "form_template_type": FormTemplateType.CATALYTIC_PE_VC_INTAKE,
            "mandatory_form_requirements": [
                "Alignment with Net Zero Investment Framework (NZIF) or COP31 Action Agenda pillars",
                "High scalability and institutional investor investability",
                "Transparent emissions accounting & transition credibility",
                "Public-private partnership or multi-level implementation impact",
            ],
            "exclusion_rules": ["Fossil-fuel expansion incompatible with 1.5C pathways"],
            "recommended_ai_model_type": AIModelArchitecture.RAG,
            "ai_model_rationale": "RAG synthesizes investor pitches aligned to IIGCC NZIF standards and Bloomberg Philanthropies' COP31 Action Agenda priorities.",
            "verification_source_url": "https://www.bloomberg.org/press/cop31-presidency-and-bloomberg-philanthropies-announce-partnership-to-advance-climate-action-ahead-of-cop31-in-antalya/",
        },
    ]

    # Add 4 more verified COP31 participating global banks from the Nov 13 2026 COP31 participant analysis
    # (JPMorganChase, Citigroup, Barclays, MUFG) -> Total = 40 verified COP31 investors & banks!
    raw_items.extend(
        [
            {
                "investor_id": "inv_jpmorgan_chase",
                "name": "JPMorgan Chase (Green Economy & Sustainable Finance)",
                "short_name": "JPMorgan Chase",
                "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
                "hq_country": "United States",
                "geographic_focus": ["Global", "North America", "Europe", "EMEA", "Asia-Pacific", "Latin America"],
                "cop31_antalya_role": "Major global bank with accredited delegation at COP31 Antalya participating in global finance & carbon/transition markets",
                "cop31_verified_2026_commitment": "Green Economy Banking, sustainable development finance ($2.5T 2021-2030 target incl. $1T green initiatives), green bonds & clean tech advisory",
                "financing_instruments": ["Green Bond Underwriting", "Corporate Transition Loan", "Project Finance", "Climate-Tech Commercial Banking", "Tax Equity / Blended Finance"],
                "typical_ticket_min_usd": 15_000_000,
                "typical_ticket_max_usd": 500_000_000,
                "target_sectors": ["Renewable Energy", "Electrification & Grid", "Climate-Tech Innovation", "Industrial Decarbonization", "Carbon Markets & Article 6"],
                "eligible_applicant_types": ["Large Corporate", "Project SPV", "Climate-Tech Startup", "Financial Intermediary"],
                "application_portal_url": "https://www.jpmorgan.com/solutions/banking/green-economy-banking",
                "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
                "mandatory_form_requirements": [
                    "ICMA GBP / LMA GLP sustainable finance use-of-proceeds documentation",
                    "Audited financial statements & corporate credit rating/underwriting",
                    "GHG emissions baseline & decarbonization KPIs",
                    "Environmental & social risk assessment",
                ],
                "exclusion_rules": ["Mountaintop coal removal", "Unpermitted environmental violations"],
                "recommended_ai_model_type": AIModelArchitecture.RAG,
                "ai_model_rationale": "RAG matches corporate/clean-tech borrowers to JPMorgan's Green Economy Banking and sustainable capital-markets guidelines.",
                "verification_source_url": "https://www.theguardian.com/environment/2026/nov/13/cop31-companies-and-groups-linked-to-fossil-fuels-delegations",
            },
            {
                "investor_id": "inv_citigroup",
                "name": "Citigroup (Citi Sustainable Finance & Transition)",
                "short_name": "Citigroup",
                "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
                "hq_country": "United States",
                "geographic_focus": ["Global", "Emerging Markets", "EMEA", "Türkiye", "Asia-Pacific", "Latin America", "North America"],
                "cop31_antalya_role": "Major global bank with accredited delegation at COP31 Antalya active in emerging-market transition & blended finance",
                "cop31_verified_2026_commitment": "$1T sustainable finance goal (2021–2030) spanning renewable project finance, green bonds, water/adaptation & emerging-market blended debt",
                "financing_instruments": ["Green Bond Underwriting", "Sustainability-Linked Loan (SLL)", "Emerging-Market Blended Debt", "Green Trade Finance", "Project Finance"],
                "typical_ticket_min_usd": 15_000_000,
                "typical_ticket_max_usd": 500_000_000,
                "target_sectors": ["Renewable Energy", "Industrial Decarbonization", "Water & Climate Adaptation", "Clean Transport", "Electrification & Grid"],
                "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary", "Sovereign/Government"],
                "application_portal_url": "https://www.citigroup.com/global/about-us/esg",
                "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
                "mandatory_form_requirements": [
                    "Citi Environmental and Social Risk Management (ESRM) & Equator Principles",
                    "ICMA / LMA sustainable finance alignment & SPT definitions",
                    "Second-Party Opinion (for labeled debt issuances)",
                    "Credit & FX risk mitigation structure",
                ],
                "exclusion_rules": ["New thermal coal power plants", "Equator Principles non-compliance"],
                "recommended_ai_model_type": AIModelArchitecture.RAG,
                "ai_model_rationale": "RAG retrieves Citi's ESRM, blended debt, and green-bond criteria to populate transition and use-of-proceeds sections.",
                "verification_source_url": "https://countercurrents.org/2026/11/climate-summit-to-save-the-planet-yet-polluters-crowd-the-halls-103-polluting-entities-at-cop31-2-2-trillion-in-fossil-fuel-financing/",
            },
            {
                "investor_id": "inv_barclays",
                "name": "Barclays (Sustainable & Transition Finance)",
                "short_name": "Barclays",
                "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
                "hq_country": "United Kingdom",
                "geographic_focus": ["Global", "United Kingdom", "Europe", "North America", "EMEA", "Asia-Pacific"],
                "cop31_antalya_role": "Major international bank delegation at COP31 Antalya focused on transition finance & climate-tech venture capital",
                "cop31_verified_2026_commitment": "$1T Sustainable and Transition Finance target by 2030 + £500M Sustainable Impact Capital mandate for climate-tech startups",
                "financing_instruments": ["Transition Finance Loan", "Green Bond Underwriting", "Climate-Tech Venture Equity", "Sustainability-Linked Loan"],
                "typical_ticket_min_usd": 5_000_000,
                "typical_ticket_max_usd": 400_000_000,
                "target_sectors": ["Industrial Decarbonization", "Climate-Tech Innovation", "Renewable Energy", "Energy Storage", "Clean Transport"],
                "eligible_applicant_types": ["Large Corporate", "Climate-Tech Startup", "Project SPV", "Mid-Cap Enterprise"],
                "application_portal_url": "https://www.ib.barclays/our-insights/sustainable-finance.html",
                "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
                "mandatory_form_requirements": [
                    "Barclays Transition Finance Framework (TFF) eligibility",
                    "Verified corporate decarbonization plan & KPIs",
                    "Commercial creditworthiness or Series A-C venture traction",
                    "External assurance / SPO for labeled facilities",
                ],
                "exclusion_rules": ["New upstream oil & gas projects", "Thermal coal expansion"],
                "recommended_ai_model_type": AIModelArchitecture.RAG,
                "ai_model_rationale": "RAG draws on Barclays' Transition Finance Framework and Sustainable Impact Capital mandate to tailor corporate and startup applications.",
                "verification_source_url": "https://www.theguardian.com/environment/2026/nov/13/cop31-companies-and-groups-linked-to-fossil-fuels-delegations",
            },
            {
                "investor_id": "inv_mufg",
                "name": "Mitsubishi UFJ Financial Group (MUFG)",
                "short_name": "MUFG",
                "category": InvestorCategory.GLOBAL_COMMERCIAL_BANK,
                "hq_country": "Japan",
                "geographic_focus": ["Global", "Asia-Pacific", "EMEA", "Türkiye", "Americas", "Europe"],
                "cop31_antalya_role": "Major Japanese megabank delegation at COP31 Antalya active in global renewable project finance & industrial transition",
                "cop31_verified_2026_commitment": "¥100 trillion (~$650B+) cumulative sustainable finance target (FY2019–FY2030) spanning renewable project finance, hydrogen/ammonia & transition loans",
                "financing_instruments": ["Renewable Project Finance Debt", "Transition Loan", "Green Bond Underwriting", "Export Credit Agency (ECA)-Backed Green Loan"],
                "typical_ticket_min_usd": 20_000_000,
                "typical_ticket_max_usd": 500_000_000,
                "target_sectors": ["Renewable Energy", "Industrial Decarbonization", "Hydrogen & Sustainable Fuels", "Electrification & Grid", "Energy Storage"],
                "eligible_applicant_types": ["Large Corporate", "Project SPV", "Financial Intermediary"],
                "application_portal_url": "https://www.mufg.jp/english/csr/sustainable_finance/index.html",
                "form_template_type": FormTemplateType.GLOBAL_COMMERCIAL_BANK_TRANSITION,
                "mandatory_form_requirements": [
                    "MUFG Environmental and Social Policy Framework & Equator Principles",
                    "Transition Finance eligibility (METI / ICMA Climate Transition Finance Handbook)",
                    "Long-term PPA / EPC bankability & DSCR profile",
                    "External SPO or transition verification",
                ],
                "exclusion_rules": ["New unabated coal-fired power plants"],
                "recommended_ai_model_type": AIModelArchitecture.RAG,
                "ai_model_rationale": "RAG aligns renewable and hydrogen/transition project-finance filings with MUFG's Climate Transition Finance Handbook criteria.",
                "verification_source_url": "https://countercurrents.org/2026/11/climate-summit-to-save-the-planet-yet-polluters-crowd-the-halls-103-polluting-entities-at-cop31-2-2-trillion-in-fossil-fuel-financing/",
            },
        ]
    )

    # Validate base 44 records, enrich with V1 priority/status metadata, and merge 22 additional Business Forum WG & Ecosystem entities -> 66 total!
    base_enriched = [enrich_investor_record(InvestorRecord.model_validate(item)) for item in raw_items]
    extra_entities = get_additional_v1_and_ecosystem_entities()
    all_entities = base_enriched + extra_entities

    # Sort cleanly by Priority Tier (Tier A -> Tier B -> Tier C) then AI Priority (P1 -> P2 -> P3)
    tier_order = {
        "Tier A — Approach Immediately": 0,
        "Tier B — Core Follow-Up": 1,
        "Tier C — Ecosystem / Strategic": 2,
    }
    prio_order = {"P1": 0, "P2": 1, "P3": 2}
    all_entities.sort(
        key=lambda x: (
            tier_order.get(x.priority_tier, 9),
            prio_order.get(x.ai_rag_priority, 9),
            x.name.lower(),
        )
    )
    assert len(all_entities) == 66
    return all_entities


def write_sample_applicant_projects(path: Path) -> None:
    """Create 3 realistic multi-sector climate applicant projects covering Industry/Energy, Agri-Adaptation SME, and Climate-Tech/Grid."""
    projects = {
        "schema_version": "1.0.0",
        "description": "Multi-sector sample applicant profiles for testing the COP31 Per-Investor KAG/RAG Automated Form-Filling System",
        "projects": [
            {
                "project_id": "proj_anatolia_green_steel_solar",
                "project_title": "Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project",
                "organization_name": "Anatolia Clean Metallurgy A.Ş.",
                "applicant_type": "Large Corporate",
                "country": "Türkiye",
                "region": "EMEA",
                "tax_or_registration_id": "VKN-4829103847",
                "contact_email": "finance@anatoliacleanmetal.example.tr",
                "contact_phone": "+90 242 555 0194",
                "iban_or_account": "TR330006100519786457841326",
                "primary_sector": "Industrial Decarbonization",
                "secondary_sectors": ["Renewable Energy", "Energy Storage", "EU CBAM Export Compliance"],
                "requested_amount_usd": 45000000,
                "total_project_cost_usd": 95000000,
                "co_financing_committed_usd": 30000000,
                "preferred_instruments": ["Senior Debt", "Green Investment Loan", "Blended Finance"],
                "project_stage": "Ready-to-Build",
                "implementation_years": 4,
                "estimated_ghg_reduction_tco2e_per_year": 185000.0,
                "adaptation_beneficiaries": 1200,
                "annual_revenue_usd": 240000000.0,
                "ebitda_usd": 42000000.0,
                "expected_irr_percent": 15.8,
                "has_eia_and_permits": True,
                "has_paris_alignment_assessment": True,
                "has_nda_no_objection_letter": False,
                "has_second_party_opinion": True,
                "has_kgf_or_collateral": True,
                "shariah_compliant_structure": False,
                "women_or_youth_led": False,
                "eu_cbam_exporter": True,
                "fossil_fuel_involvement": False,
                "project_summary": "Retrofitting a major Turkish steel rolling facility to 100% renewable-powered electric-arc furnace operation paired with 120 MW captive solar PV and 60 MWh lithium-iron-phosphate battery storage to achieve EU CBAM compliance. Contact finance@anatoliacleanmetal.example.tr for technical annex.",
                "climate_rationale": "Cuts steelmaking Scope 1 and Scope 2 carbon intensity by 62% (185,000 tCO2e/year avoided), directly supporting Türkiye's 2035 NDC and TIDIP industrial decarbonization targets.",
                "technology_and_innovation": "High-efficiency scrap preheating electric-arc furnace integrated with grid-forming 60 MWh BESS, digital twin energy dispatch, and ISO 14064 real-time carbon MRV.",
                "esg_and_social_impact": "Creates 320 green engineering jobs, zero coal usage, closed-loop 85% process water recycling, and formal workforce reskilling aligned with Just Transition principles.",
                "key_risks_and_mitigants": "Grid curtailment risk mitigated via 60 MWh BESS; FX mismatch mitigated by EUR-denominated EU green-steel export offtake contracts covering 75% of output; EPC turnkey fixed-price contract.",
            },
            {
                "project_id": "proj_antalya_agri_adaptation_sme",
                "project_title": "Antalya Solar-Powered Precision Drip Irrigation & Climate-Resilient Cold Chain",
                "organization_name": "Akdeniz Yeşil Tarım Kooperatifi Ltd.",
                "applicant_type": "SME",
                "country": "Türkiye",
                "region": "EMEA",
                "tax_or_registration_id": "VKN-7391046281",
                "contact_email": "info@akdenizyesiltarim.example.tr",
                "contact_phone": "+90 242 555 0821",
                "iban_or_account": "TR640001001234567890123456",
                "primary_sector": "Sustainable Agriculture & Water",
                "secondary_sectors": ["Climate Adaptation & Resilience", "Renewable Energy", "SME Green Transition", "Women-Led Green Enterprise"],
                "requested_amount_usd": 1800000,
                "total_project_cost_usd": 2600000,
                "co_financing_committed_usd": 500000,
                "preferred_instruments": ["SME Green Transformation Loan", "KGF-Backed Green Loan", "Grant"],
                "project_stage": "Operational Expansion",
                "implementation_years": 3,
                "estimated_ghg_reduction_tco2e_per_year": 4200.0,
                "adaptation_beneficiaries": 14500,
                "annual_revenue_usd": 6400000.0,
                "ebitda_usd": 1150000.0,
                "expected_irr_percent": 18.4,
                "has_eia_and_permits": True,
                "has_paris_alignment_assessment": False,
                "has_nda_no_objection_letter": True,
                "has_second_party_opinion": False,
                "has_kgf_or_collateral": True,
                "shariah_compliant_structure": True,
                "women_or_youth_led": True,
                "eu_cbam_exporter": True,
                "fossil_fuel_involvement": False,
                "project_summary": "Women-led Mediterranean agricultural SME deploying IoT soil-moisture precision drip irrigation across 1,800 hectares in Antalya alongside 2.5 MW agrivoltaic rooftop solar and low-GWP cold storage to cut water consumption by 48%.",
                "climate_rationale": "Addresses severe Mediterranean drought and extreme heat risks by reducing groundwater extraction by 4.1 million m3/year while replacing diesel irrigation pumps with solar PV (4,200 tCO2e/year avoided).",
                "technology_and_innovation": "LoRaWAN soil-moisture & evapotranspiration sensors automated with solar pumping and natural-refrigerant cold chain extending export shelf life by 40%.",
                "esg_and_social_impact": "Women-owned enterprise employing 68% female agricultural technicians; directly strengthens climate resilience for 14,500 rural residents and 420 smallholder farms.",
                "key_risks_and_mitigants": "Weather yield variability mitigated by parametric agricultural insurance (TARSİM); credit collateral backed by KGF Green Transformation Guarantee and confirmed EU organic supermarket buyer contracts.",
            },
            {
                "project_id": "proj_em_grid_flex_storage",
                "project_title": "Afro-Med Distributed Grid Storage & Clean Electrification Virtual Power Plant",
                "organization_name": "HeliosGrid Flexibility SPV",
                "applicant_type": "Project SPV",
                "country": "Egypt",
                "region": "Africa",
                "tax_or_registration_id": "REG-EG-9928410",
                "contact_email": "deals@heliosgrid.example.com",
                "contact_phone": "+20 2 5550 4421",
                "iban_or_account": None,
                "primary_sector": "Electrification & Grid",
                "secondary_sectors": ["Energy Storage", "Renewable Energy", "Climate-Tech Innovation"],
                "requested_amount_usd": 18000000,
                "total_project_cost_usd": 36000000,
                "co_financing_committed_usd": 10000000,
                "preferred_instruments": ["Blended Finance", "Equity", "Senior Debt", "Catalytic First-Loss Capital"],
                "project_stage": "Feasibility",
                "implementation_years": 5,
                "estimated_ghg_reduction_tco2e_per_year": 92000.0,
                "adaptation_beneficiaries": 85000,
                "annual_revenue_usd": 9200000.0,
                "ebitda_usd": 4100000.0,
                "expected_irr_percent": 16.5,
                "has_eia_and_permits": False,
                "has_paris_alignment_assessment": True,
                "has_nda_no_objection_letter": True,
                "has_second_party_opinion": False,
                "has_kgf_or_collateral": False,
                "shariah_compliant_structure": True,
                "women_or_youth_led": False,
                "eu_cbam_exporter": False,
                "fossil_fuel_involvement": False,
                "project_summary": "Deploying 90 MWh of modular utility-connected battery energy storage and AI virtual power plant dispatch across industrial parks in Egypt to displace peaking diesel/gas generation and stabilize solar grid integration.",
                "climate_rationale": "Enables 140 MW of additional solar absorption without curtailment and displaces 92,000 tCO2e/year of peaking fossil generation, directly advancing the COP31 35-by-35 Global Electrification Pledge.",
                "technology_and_innovation": "Modular containerized LFP storage orchestrated by machine-learning grid frequency forecasting and automated demand-response telemetry.",
                "esg_and_social_impact": "Eliminates blackouts for 85,000 industrial/community power users, reduces urban diesel particulate emissions, and trains 150 local grid engineers.",
                "key_risks_and_mitigants": "Currency convertibility and utility offtake risk mitigated via DFI partial risk guarantee (10by30 / CIF AMPLIFi catalytic tranche) and USD-indexed industrial park power capacity contracts.",
            },
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")


def export_json_and_csv(investors: List[InvestorRecord], data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)

    json_payload = {
        "schema_version": "1.0.0",
        "summit": "UNFCCC COP31 Antalya, Türkiye (9–20 November 2026)",
        "compiled_date": "2026-11-15",
        "total_verified_investors": len(investors),
        "investors": [inv.model_dump(mode="json") for inv in investors],
    }
    (data_dir / "cop31_investors_verified.json").write_text(
        json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    csv_fields = [
        "investor_id",
        "name",
        "short_name",
        "relationship_status",
        "priority_tier",
        "ai_rag_priority",
        "greenhope_relevance",
        "ecosystem_branch",
        "category",
        "hq_country",
        "geographic_focus",
        "cop31_antalya_role",
        "cop31_verified_2026_commitment",
        "greenhope_fit_notes",
        "financing_instruments",
        "typical_ticket_min_usd",
        "typical_ticket_max_usd",
        "target_sectors",
        "eligible_applicant_types",
        "form_template_type",
        "recommended_ai_model_type",
        "knowledge_pack_slug",
        "ai_model_rationale",
        "mandatory_form_requirements",
        "exclusion_rules",
        "application_portal_url",
        "verification_source_url",
        "verification_date",
        "verification_status",
    ]
    with (data_dir / "cop31_investors_verified.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=csv_fields)
        writer.writeheader()
        for inv in investors:
            row = inv.model_dump(mode="json")
            for k in ["geographic_focus", "financing_instruments", "target_sectors", "eligible_applicant_types", "mandatory_form_requirements", "exclusion_rules"]:
                row[k] = "; ".join(row[k])
            writer.writerow({k: row[k] for k in csv_fields})


def export_formatted_excel(investors: List[InvestorRecord], xlsx_path: Path) -> None:
    """Create a publication-grade 5-sheet Excel registry with live formulas, color coding, auto-filter, and zero truncation."""
    wb = Workbook()

    # Palette (Executive Climate Finance Navy & Emerald)
    NAVY_DARK = "0F2942"
    EMERALD_DARK = "0F5132"
    EMERALD_SOFT = "E8F5E9"
    TEAL_HEADER = "155E75"
    ZEBRA_FILL = "F8FAFC"
    BORDER_GRAY = "CBD5E1"
    KAG_BG, KAG_FG = "DBEAFE", "1E3A8A"       # Blue badge for KAG
    RAG_BG, RAG_FG = "DCFCE7", "166534"       # Green badge for RAG
    HYB_BG, HYB_FG = "FEF3C7", "92400E"       # Amber badge for HYBRID_KAG_RAG

    thin_side = Side(style="thin", color=BORDER_GRAY)
    med_navy = Side(style="medium", color=NAVY_DARK)
    cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    header_border = Border(left=thin_side, right=thin_side, top=med_navy, bottom=med_navy)

    font_title = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
    font_sec = Font(name="Calibri", size=12, bold=True, color=NAVY_DARK)
    font_hdr = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_body = Font(name="Calibri", size=10, color="1E293B")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_link = Font(name="Calibri", size=9, color="0369A1", underline="single")

    fill_navy = PatternFill("solid", fgColor=NAVY_DARK)
    fill_teal = PatternFill("solid", fgColor=TEAL_HEADER)
    fill_emerald = PatternFill("solid", fgColor=EMERALD_DARK)
    fill_emerald_soft = PatternFill("solid", fgColor=EMERALD_SOFT)
    fill_zebra = PatternFill("solid", fgColor=ZEBRA_FILL)
    fill_white = PatternFill("solid", fgColor="FFFFFF")

    # =========================================================================
    # SHEET 2 FIRST (so Sheet 1 formulas reference exact row ranges!)
    # =========================================================================
    ws_reg = wb.create_sheet("COP31 Investor Registry")
    ws_reg.views.sheetView[0].showGridLines = True

    reg_headers = [
        "Investor ID",
        "Institution Name",
        "Relationship Status",
        "Priority Tier",
        "AI/RAG Priority",
        "GreenHope Relevance",
        "Ecosystem Branch",
        "Category",
        "HQ Country",
        "Geographic Focus",
        "COP31 Antalya 2026 Role",
        "Verified COP31 2026 Commitment",
        "GreenHope Fit & Attack Notes",
        "Financing Instruments",
        "Min Ticket (USD)",
        "Max Ticket (USD)",
        "Priority Climate Sectors",
        "Eligible Applicants",
        "Form Template",
        "AI Model Type",
        "Knowledge Pack",
        "Official Application Portal",
        "Verification Source (Nov 2026)",
        "Verification Status",
    ]
    ws_reg.merge_cells("A1:X1")
    ws_reg["A1"] = "GREENHOPE × UNFCCC COP31 ANTALYA (NOV 9–20, 2026) — VERIFIED INVESTOR, BANK & ECOSYSTEM MASTER REGISTRY"
    ws_reg["A1"].font = font_title
    ws_reg["A1"].fill = fill_navy
    ws_reg["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_reg.row_dimensions[1].height = 34

    ws_reg.merge_cells("A2:X2")
    ws_reg["A2"] = "Distinguishes Investor Confirmed vs. Finance Participant vs. COP31 Supporter vs. Strategic Partner | AES-256-GCM Vault Secured | Verified 2026-11-15"
    ws_reg["A2"].font = font_subtitle
    ws_reg["A2"].fill = fill_teal
    ws_reg["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_reg.row_dimensions[2].height = 22

    header_row = 4
    ws_reg.row_dimensions[header_row].height = 30
    for col_idx, h_text in enumerate(reg_headers, start=1):
        c = ws_reg.cell(row=header_row, column=col_idx, value=h_text)
        c.font = font_hdr
        c.fill = fill_navy
        c.border = header_border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    start_row = 5
    for i, inv in enumerate(investors):
        r = start_row + i
        row_fill = fill_zebra if i % 2 == 1 else fill_white
        vals = [
            inv.investor_id,
            inv.name,
            inv.relationship_status.value,
            inv.priority_tier,
            inv.ai_rag_priority,
            inv.greenhope_relevance,
            inv.ecosystem_branch.value,
            inv.category.value,
            inv.hq_country,
            ", ".join(inv.geographic_focus),
            inv.cop31_antalya_role,
            inv.cop31_verified_2026_commitment,
            inv.greenhope_fit_notes,
            ", ".join(inv.financing_instruments),
            inv.typical_ticket_min_usd,
            inv.typical_ticket_max_usd,
            ", ".join(inv.target_sectors),
            ", ".join(inv.eligible_applicant_types),
            inv.form_template_type.value,
            inv.recommended_ai_model_type.value,
            f"investors/{inv.knowledge_pack_slug}/" if inv.knowledge_pack_slug else "Central Registry",
            inv.application_portal_url,
            inv.verification_source_url,
            inv.verification_status,
        ]
        ws_reg.row_dimensions[r].height = 56
        for col_idx, val in enumerate(vals, start=1):
            c = ws_reg.cell(row=r, column=col_idx, value=val)
            c.font = font_bold if col_idx in (1, 2) else font_body
            c.fill = row_fill
            c.border = cell_border
            c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

            if col_idx == 3:
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                if val == "Investor Confirmed":
                    c.fill = PatternFill("solid", fgColor=RAG_BG)
                    c.font = Font(name="Calibri", size=9, bold=True, color=RAG_FG)
                elif val == "Finance Participant":
                    c.fill = PatternFill("solid", fgColor=KAG_BG)
                    c.font = Font(name="Calibri", size=9, bold=True, color=KAG_FG)
                elif val == "COP31 Supporter":
                    c.fill = PatternFill("solid", fgColor="FEE2E2")
                    c.font = Font(name="Calibri", size=9, bold=True, color="991B1B")
                else:
                    c.fill = PatternFill("solid", fgColor=HYB_BG)
                    c.font = Font(name="Calibri", size=9, bold=True, color=HYB_FG)
            elif col_idx == 5:
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = Font(name="Calibri", size=10, bold=True, color="991B1B" if val == "P1" else ("92400E" if val == "P2" else "475569"))
            elif col_idx in (15, 16):
                c.number_format = "$#,##0"
                c.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx == 20:
                c.alignment = Alignment(horizontal="center", vertical="center")
                if val == "KAG":
                    c.fill = PatternFill("solid", fgColor=KAG_BG)
                    c.font = Font(name="Calibri", size=10, bold=True, color=KAG_FG)
                elif val == "RAG":
                    c.fill = PatternFill("solid", fgColor=RAG_BG)
                    c.font = Font(name="Calibri", size=10, bold=True, color=RAG_FG)
                else:
                    c.fill = PatternFill("solid", fgColor=HYB_BG)
                    c.font = Font(name="Calibri", size=10, bold=True, color=HYB_FG)
            elif col_idx in (22, 23):
                c.hyperlink = str(val)
                c.font = font_link
            elif col_idx == 24:
                c.fill = fill_emerald_soft
                c.font = Font(name="Calibri", size=9, bold=True, color=EMERALD_DARK)
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    end_row = start_row + len(investors) - 1
    ws_reg.freeze_panes = "C5"
    ws_reg.auto_filter.ref = f"A4:X{end_row}"

    reg_widths = [22, 34, 22, 26, 13, 18, 26, 28, 20, 24, 34, 38, 38, 28, 16, 17, 30, 24, 26, 17, 22, 30, 30, 24]
    for idx, w in enumerate(reg_widths, start=1):
        ws_reg.column_dimensions[get_column_letter(idx)].width = w

    # =========================================================================
    # SHEET 1: EXECUTIVE SUMMARY (Live Excel Formulas!)
    # =========================================================================
    ws_sum = wb.active
    ws_sum.title = "Executive Summary"
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum.merge_cells("A1:G1")
    ws_sum["A1"] = "COP31 ANTALYA 2026 — SECURED INVESTOR REGISTRY & PER-INVESTOR KAG/RAG AI SYSTEM"
    ws_sum["A1"].font = font_title
    ws_sum["A1"].fill = fill_navy
    ws_sum["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_sum.row_dimensions[1].height = 36

    ws_sum.merge_cells("A2:G2")
    ws_sum["A2"] = "Executive Dashboard | Step 1: Verified & Encrypted Investor Vault -> Step 2: Dedicated KAG / RAG / Hybrid Model per Investor -> Step 3: Automated Form Filling"
    ws_sum["A2"].font = font_subtitle
    ws_sum["A2"].fill = fill_emerald
    ws_sum["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_sum.row_dimensions[2].height = 24

    # KPI Summary Block (Live Formulas referencing Sheet 2!)
    ws_sum["A4"] = "1. PORTFOLIO & MODEL KPI SNAPSHOT (LIVE FORMULAS)"
    ws_sum["A4"].font = font_sec
    ws_sum.row_dimensions[4].height = 24

    kpi_headers = ["KPI Metric", "Formula Value", "Description / Governance Note"]
    for c_idx, h in enumerate(kpi_headers, start=1):
        cell = ws_sum.cell(row=5, column=c_idx, value=h)
        cell.font = font_hdr
        cell.fill = fill_navy
        cell.border = header_border
        cell.alignment = Alignment(horizontal="center" if c_idx == 2 else "left", vertical="center")
    ws_sum.merge_cells("C5:G5")
    ws_sum.row_dimensions[5].height = 24

    kpis = [
        ("Total Verified COP31 Entities (Investors, Banks & Ecosystem)", f"=COUNTA('COP31 Investor Registry'!A{start_row}:A{end_row})", "0", "All 66 entities verified against Nov 2026 COP31 Antalya sources & secured in AES-256-GCM vault"),
        ("Investor Confirmed Entities", f"=COUNTIF('COP31 Investor Registry'!C{start_row}:C{end_row},\"Investor Confirmed\")", "0", "Confirmed active funding institutions (distinct from COP31 Climate Supporters)"),
        ("COP31 Supporters / Strategic Partners (Non-Direct Funders)", f"=COUNTIF('COP31 Investor Registry'!C{start_row}:C{end_row},\"COP31 Supporter\")+COUNTIF('COP31 Investor Registry'!C{start_row}:C{end_row},\"Potential Strategic Partner\")", "0", "Explicitly separated so AI never mislabels supporters (Siemens, Cisco, IKEA, etc.) as direct funders"),
        ("Priority P1 AI/RAG Targets", f"=COUNTIF('COP31 Investor Registry'!E{start_row}:E{end_row},\"P1\")", "0", "First-wave GreenHope targets with dedicated 13-file Investor Knowledge Packs"),
        ("KAG / RAG / HYBRID Scope Counts (KAG / RAG / HYBRID)", f"=COUNTIF('COP31 Investor Registry'!T{start_row}:T{end_row},\"KAG\")", "0", "Deterministic KAG scopes (plus RAG & Hybrid scopes mapped in Sheet 3)"),
        ("Average Max Single-Ticket Capacity (USD)", f"=AVERAGE('COP31 Investor Registry'!P{start_row}:P{end_row})", "$#,##0", "Average single-investor ceiling before co-financing/syndication"),
        ("Verified COP31 Antalya 2026 Records", f"=COUNTIF('COP31 Investor Registry'!X{start_row}:X{end_row},\"VERIFIED_COP31_ANTALYA_2026\")", "0", "100% of records cryptographically hashed, Merkle-rooted & signed in Step 1 Vault"),
    ]
    for idx, (label, formula, num_fmt, note) in enumerate(kpis, start=6):
        ws_sum.row_dimensions[idx].height = 24
        ws_sum.merge_cells(start_row=idx, start_column=3, end_row=idx, end_column=7)
        c1 = ws_sum.cell(row=idx, column=1, value=label)
        c2 = ws_sum.cell(row=idx, column=2, value=formula)
        c3 = ws_sum.cell(row=idx, column=3, value=note)
        fill = fill_zebra if idx % 2 == 1 else fill_white
        for c in (c1, c2, c3):
            c.fill = fill
            c.border = cell_border
        c1.font = font_bold
        c2.font = Font(name="Calibri", size=11, bold=True, color=EMERALD_DARK)
        c2.number_format = num_fmt
        c2.alignment = Alignment(horizontal="right", vertical="center")
        c3.font = font_body
        c3.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Breakdown by Investor Category (Live COUNTIF + AVERAGEIF formulas!)
    ws_sum["A15"] = "2. BREAKDOWN BY COP31 INVESTOR / BANK CATEGORY"
    ws_sum["A15"].font = font_sec
    ws_sum.row_dimensions[15].height = 24

    cat_headers = ["Investor Category", "Count", "% Share", "KAG", "RAG", "HYBRID", "Avg Max Ticket (USD)"]
    for c_idx, h in enumerate(cat_headers, start=1):
        cell = ws_sum.cell(row=16, column=c_idx, value=h)
        cell.font = font_hdr
        cell.fill = fill_teal
        cell.border = header_border
        cell.alignment = Alignment(horizontal="center" if c_idx > 1 else "left", vertical="center")
    ws_sum.row_dimensions[16].height = 24

    categories = [c.value for c in InvestorCategory]
    cat_start = 17
    for offset, cat_name in enumerate(categories):
        r = cat_start + offset
        ws_sum.row_dimensions[r].height = 22
        row_fill = fill_zebra if offset % 2 == 1 else fill_white
        formulas = [
            cat_name,
            f"=COUNTIF('COP31 Investor Registry'!H{start_row}:H{end_row},A{r})",
            f"=B{r}/$B$6",
            f"=COUNTIFS('COP31 Investor Registry'!H{start_row}:H{end_row},A{r},'COP31 Investor Registry'!T{start_row}:T{end_row},\"KAG\")",
            f"=COUNTIFS('COP31 Investor Registry'!H{start_row}:H{end_row},A{r},'COP31 Investor Registry'!T{start_row}:T{end_row},\"RAG\")",
            f"=COUNTIFS('COP31 Investor Registry'!H{start_row}:H{end_row},A{r},'COP31 Investor Registry'!T{start_row}:T{end_row},\"HYBRID_KAG_RAG\")",
            f"=IFERROR(AVERAGEIF('COP31 Investor Registry'!H{start_row}:H{end_row},A{r},'COP31 Investor Registry'!P{start_row}:P{end_row}),0)",
        ]
        for c_idx, val in enumerate(formulas, start=1):
            c = ws_sum.cell(row=r, column=c_idx, value=val)
            c.fill = row_fill
            c.border = cell_border
            c.font = font_bold if c_idx == 1 else font_body
            if c_idx == 2 or c_idx in (4, 5, 6):
                c.number_format = "0"
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx == 3:
                c.number_format = "0.0%"
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx == 7:
                c.number_format = "$#,##0"
                c.alignment = Alignment(horizontal="right", vertical="center")

    tot_r = cat_start + len(categories)
    ws_sum.row_dimensions[tot_r].height = 24
    tot_vals = [
        "TOTAL",
        f"=SUM(B{cat_start}:B{tot_r-1})",
        f"=SUM(C{cat_start}:C{tot_r-1})",
        f"=SUM(D{cat_start}:D{tot_r-1})",
        f"=SUM(E{cat_start}:E{tot_r-1})",
        f"=SUM(F{cat_start}:F{tot_r-1})",
        f"=AVERAGE('COP31 Investor Registry'!P{start_row}:P{end_row})",
    ]
    for c_idx, val in enumerate(tot_vals, start=1):
        c = ws_sum.cell(row=tot_r, column=c_idx, value=val)
        c.fill = fill_emerald_soft
        c.font = font_bold
        c.border = header_border
        if c_idx in (2, 4, 5, 6):
            c.number_format = "0"
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif c_idx == 3:
            c.number_format = "0.0%"
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif c_idx == 7:
            c.number_format = "$#,##0"
            c.alignment = Alignment(horizontal="right", vertical="center")

    # Step 1 -> Step 2 -> Step 3 Workflow Guide
    wf_row = tot_r + 2
    ws_sum[f"A{wf_row}"] = "3. TWO-STAGE SECURED AI ARCHITECTURE WORKFLOW"
    ws_sum[f"A{wf_row}"].font = font_sec
    ws_sum.row_dimensions[wf_row].height = 24
    steps = [
        ("Step 1: Verify & Secure Investor Registry", "Validate all COP31 banks/investors via Pydantic -> Compute SHA-256 + Merkle Root -> Sign Manifest with HMAC-SHA256 -> Encrypt at rest with AES-256-GCM (PBKDF2 600k iterations) -> Enforce RBAC & Hash-Chained Audit Log."),
        ("Step 2: Create Per-Investor KAG/RAG Models", "Decrypt ONLY verified Step-1 Vault -> Derive unique 256-bit HKDF-SHA256 tenant subkey per investor -> Build isolated Knowledge Graph (KAG), TF-IDF/MMR Vector Corpus (RAG), or Hybrid KAG+RAG artifact directory under investor_models/<investor_id>/."),
        ("Step 3: Automated Form Filling & Screening", "Redact applicant PII (VKN/IBAN/email/phone) -> Screen & rank all COP31 models -> Populate target investor's exact application form with KAG reasoning traces, RAG citations, confidence scores & human compliance checklist."),
    ]
    for idx, (s_title, s_desc) in enumerate(steps, start=wf_row + 1):
        ws_sum.row_dimensions[idx].height = 36
        ws_sum.merge_cells(start_row=idx, start_column=2, end_row=idx, end_column=7)
        c1 = ws_sum.cell(row=idx, column=1, value=s_title)
        c2 = ws_sum.cell(row=idx, column=2, value=s_desc)
        c1.font = font_bold
        c1.fill = fill_emerald_soft
        c1.border = cell_border
        c1.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c2.font = font_body
        c2.fill = fill_white
        c2.border = cell_border
        c2.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    sum_widths = [38, 16, 14, 12, 12, 12, 24]
    for idx, w in enumerate(sum_widths, start=1):
        ws_sum.column_dimensions[get_column_letter(idx)].width = w

    # =========================================================================
    # SHEET 3: AI MODEL ARCHITECTURE MATRIX (All Per-Investor Models)
    # =========================================================================
    ws_mod = wb.create_sheet("AI Model Architecture Matrix")
    ws_mod.views.sheetView[0].showGridLines = True
    ws_mod.merge_cells("A1:I1")
    ws_mod["A1"] = "STEP 2: PER-INVESTOR KAG / RAG / HYBRID AI MODEL SPECIFICATION MATRIX"
    ws_mod["A1"].font = font_title
    ws_mod["A1"].fill = fill_navy
    ws_mod["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_mod.row_dimensions[1].height = 32

    mod_headers = [
        "Investor ID",
        "Institution",
        "AI Model Type",
        "Isolated Tenant Namespace",
        "Artifact Directory",
        "KAG Graph Enabled?",
        "RAG Vector Corpus Enabled?",
        "Assigned Form Template",
        "Why KAG vs RAG vs Hybrid?",
    ]
    ws_mod.row_dimensions[3].height = 28
    for c_idx, h in enumerate(mod_headers, start=1):
        c = ws_mod.cell(row=3, column=c_idx, value=h)
        c.font = font_hdr
        c.fill = fill_teal
        c.border = header_border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i, inv in enumerate(investors):
        r = 4 + i
        ws_mod.row_dimensions[r].height = 38
        arch = inv.recommended_ai_model_type.value
        has_kag = "YES (NetworkX KG)" if arch in ("KAG", "HYBRID_KAG_RAG") else "NO"
        has_rag = "YES (TF-IDF + MMR)" if arch in ("RAG", "HYBRID_KAG_RAG") else "NO"
        row_vals = [
            inv.investor_id,
            inv.name,
            arch,
            f"tenant::{inv.investor_id}",
            f"investor_models/{inv.investor_id}/",
            has_kag,
            has_rag,
            inv.form_template_type.value,
            inv.ai_model_rationale,
        ]
        fill = fill_zebra if i % 2 == 1 else fill_white
        for c_idx, val in enumerate(row_vals, start=1):
            c = ws_mod.cell(row=r, column=c_idx, value=val)
            c.font = font_bold if c_idx in (1, 2) else font_body
            c.fill = fill
            c.border = cell_border
            c.alignment = Alignment(horizontal="center" if c_idx in (3, 6, 7) else "left", vertical="center", wrap_text=True)
            if c_idx == 3:
                if val == "KAG":
                    c.fill = PatternFill("solid", fgColor=KAG_BG)
                    c.font = Font(name="Calibri", size=10, bold=True, color=KAG_FG)
                elif val == "RAG":
                    c.fill = PatternFill("solid", fgColor=RAG_BG)
                    c.font = Font(name="Calibri", size=10, bold=True, color=RAG_FG)
                else:
                    c.fill = PatternFill("solid", fgColor=HYB_BG)
                    c.font = Font(name="Calibri", size=10, bold=True, color=HYB_FG)

    ws_mod.freeze_panes = "C4"
    ws_mod.auto_filter.ref = f"A3:I{3 + len(investors)}"
    mod_widths = [24, 34, 18, 26, 30, 20, 22, 30, 48]
    for idx, w in enumerate(mod_widths, start=1):
        ws_mod.column_dimensions[get_column_letter(idx)].width = w

    # =========================================================================
    # SHEET 4: FORM SCHEMA CATALOG
    # =========================================================================
    ws_frm = wb.create_sheet("Form Schema Catalog")
    ws_frm.views.sheetView[0].showGridLines = True
    ws_frm.merge_cells("A1:G1")
    ws_frm["A1"] = "AUTOMATED FORM-FILLING TEMPLATES & FIELD-LEVEL KAG/RAG STRATEGIES"
    ws_frm["A1"].font = font_title
    ws_frm["A1"].fill = fill_navy
    ws_frm["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_frm.row_dimensions[1].height = 32

    frm_headers = ["Template ID", "Form Section", "Field ID", "Field Label", "Field Type", "AI Strategy", "Field Requirements & Grounding Description"]
    ws_frm.row_dimensions[3].height = 26
    for c_idx, h in enumerate(frm_headers, start=1):
        c = ws_frm.cell(row=3, column=c_idx, value=h)
        c.font = font_hdr
        c.fill = fill_teal
        c.border = header_border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    fr_row = 4
    for tpl in FORM_TEMPLATES.values():
        for fld in tpl.fields:
            ws_frm.row_dimensions[fr_row].height = 32
            fill = fill_zebra if fr_row % 2 == 1 else fill_white
            vals = [
                tpl.template_id.value,
                fld.section,
                fld.field_id,
                fld.label,
                fld.field_type,
                fld.generation_strategy,
                fld.description,
            ]
            for c_idx, val in enumerate(vals, start=1):
                c = ws_frm.cell(row=fr_row, column=c_idx, value=val)
                c.font = font_bold if c_idx in (1, 4) else font_body
                c.fill = fill
                c.border = cell_border
                c.alignment = Alignment(horizontal="center" if c_idx in (5, 6) else "left", vertical="center", wrap_text=True)
            fr_row += 1

    ws_frm.freeze_panes = "A4"
    ws_frm.auto_filter.ref = f"A3:G{fr_row - 1}"
    frm_widths = [30, 24, 28, 36, 16, 18, 52]
    for idx, w in enumerate(frm_widths, start=1):
        ws_frm.column_dimensions[get_column_letter(idx)].width = w

    # =========================================================================
    # SHEET 5: SECURITY & VERIFICATION CONTROLS
    # =========================================================================
    ws_sec = wb.create_sheet("Security & Verification")
    ws_sec.views.sheetView[0].showGridLines = True
    ws_sec.merge_cells("A1:D1")
    ws_sec["A1"] = "STEP 1 SECURITY ARCHITECTURE — ENCRYPTION, INTEGRITY, RBAC, PII & TENANT ISOLATION"
    ws_sec["A1"].font = font_title
    ws_sec["A1"].fill = fill_navy
    ws_sec["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_sec.row_dimensions[1].height = 32

    sec_headers = ["Security Control Domain", "Implementation Standard", "Workspace Module / Artifact", "Protection Guarantee"]
    ws_sec.row_dimensions[3].height = 26
    for c_idx, h in enumerate(sec_headers, start=1):
        c = ws_sec.cell(row=3, column=c_idx, value=h)
        c.font = font_hdr
        c.fill = fill_emerald
        c.border = header_border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    sec_rows = [
        ("Encryption at Rest", "AES-256-GCM (NIST SP 800-38D) with Associated Authenticated Data (AAD)", "src/security/crypto_engine.py -> data/secured_vault/cop31_investors.vault.enc", "Confidentiality + authenticity; any bit flip in ciphertext or AAD fails GCM tag verification immediately."),
        ("Master Key Derivation", "PBKDF2-HMAC-SHA256 (600,000 iterations + 128-bit CSPRNG salt)", "src/security/vault.py -> data/secured_vault/key_policy.json", "Resists brute-force attacks; master passphrase never persisted to disk (env/KMS injection only)."),
        ("Registry Tamper Detection", "Per-Record SHA-256 + Binary Merkle Tree Root + HMAC-SHA256 Manifest", "data/secured_vault/registry_integrity.manifest.json", f"Step 2 Model Factory refuses to run unless ciphertext hash, HMAC signature, and all {len(investors)} record hashes match."),
        ("Per-Investor Tenant Isolation", "RFC 5869 HKDF-SHA256 Unique Subkey + Strict Namespace Path Guard", "src/security/tenant_guard.py -> investor_models/<investor_id>/", "Prevents cross-investor RAG/KAG data leakage; blocks path traversal and cross-tenant KG/chunk injection."),
        ("Role-Based Access Control (RBAC)", "5 Least-Privilege Roles (ADMIN, SECURITY_OFFICER, MODEL_ENGINEER, FORM_OPERATOR, AUDITOR)", "src/security/vault.py (ROLE_PERMISSIONS)", "Enforces separation of duties across vault sealing, verification, model building, form filling, and auditing."),
        ("Applicant PII Redaction", "Automated Regex Sanitization & Identifier Masking (VKN/TCKN, IBAN, Email, Phone)", "src/security/tenant_guard.py (PIIRedactor)", "Prevents sensitive applicant PII from entering AI retrieval logs or external LLM API prompts."),
        ("Tamper-Evident Audit Trail", "Append-Only SHA-256 Hash-Chained JSONL Ledger (prev_hash -> entry_hash)", "data/secured_vault/audit_log.jsonl", "Records every seal, verify, read, access denial, model build, and form fill; detectable via verify_audit_chain()."),
    ]
    for i, vals in enumerate(sec_rows):
        r = 4 + i
        ws_sec.row_dimensions[r].height = 42
        fill = fill_zebra if i % 2 == 1 else fill_white
        for c_idx, val in enumerate(vals, start=1):
            c = ws_sec.cell(row=r, column=c_idx, value=val)
            c.font = font_bold if c_idx == 1 else font_body
            c.fill = fill
            c.border = cell_border
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    sec_widths = [28, 36, 42, 54]
    for idx, w in enumerate(sec_widths, start=1):
        ws_sec.column_dimensions[get_column_letter(idx)].width = w

    xlsx_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(xlsx_path)


def main() -> None:
    investors = get_verified_cop31_investors()
    data_dir = PROJECT_ROOT / "data"
    export_json_and_csv(investors, data_dir)
    export_formatted_excel(investors, data_dir / "COP31_Investors_Banks_Registry.xlsx")
    write_sample_applicant_projects(data_dir / "sample_applicant_projects.json")
    print(f"Built verified COP31 investor registry with {len(investors)} institutions.")
    arch_counts = {}
    for inv in investors:
        arch_counts[inv.recommended_ai_model_type.value] = arch_counts.get(inv.recommended_ai_model_type.value, 0) + 1
    print("AI Model Breakdown:", arch_counts)


if __name__ == "__main__":
    main()
