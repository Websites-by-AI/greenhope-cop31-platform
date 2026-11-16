# Auto-Filled COP31 Investor Application Packet

- **Submission ID:** `sub_inv_ifc_proj_anatolia_green_steel_solar_a3d9b26a`
- **Target Investor / Bank:** International Finance Corporation (IFC) (`inv_ifc`)
- **AI Model Architecture:** `HYBRID_KAG_RAG`
- **Form Template:** Multilateral Development Bank (MDB) Climate Project Concept Note (`MDB_CONCEPT_NOTE`)
- **Applicant Project:** Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (`proj_anatolia_green_steel_solar`)
- **Security Controls:** Tenant Isolation Verified=`True` | PII Redacted=`True`
- **Eligibility Decision:** `ELIGIBLE` (Fit Score: **97.0/100**, Recommended Instrument: **Senior Debt**)
- **Completion Rate:** **100.0%** | **Average Confidence:** **0.94**
- **Synthesis Backend:** `deterministic-grounded-synthesizer-v1`

## Eligibility Screening Summary

- [PASS] Applicant type 'Large Corporate' matched via ACCEPTS_APPLICANT (Large Corporate, Project SPV, Financial Intermediary, Growth-Stage Private Enterprise).
- [PASS] Geography 'Türkiye (EMEA)' covered via COVERS_REGION (Global, Emerging Markets, Developing Countries, Türkiye, Africa, Asia, Latin America).
- [PASS] Sector alignment verified via FUNDS_SECTOR: Energy Storage, Industrial Decarbonization, Renewable Energy.
- [PASS] Requested ticket $45,000,000 fits within bounds ($10,000,000–$250,000,000).
- [PASS] Instrument match via OFFERS_INSTRUMENT: 'Senior Debt'.
- [PASS] Exclusion list screening passed (no prohibited coal/unabated fossil-fuel activities).
- [WARN] Missing mandatory NDA / Operational Focal Point No-Objection Letter (required before final submission).

## Auto-Filled Form Fields

### 1. Identification

**Project Title & Legal Sponsor** (`project_title`) — Status: `FILLED` | Confidence: `0.98` | Mode: `HYBRID_KAG_RAG (KAG-primary)`
> Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project | Sponsor: Anatolia Clean Metallurgy A.Ş. (Large Corporate) | Jurisdiction: Türkiye (EMEA) | Primary Sector: Industrial Decarbonization
- *KAG Trace:* `inv_ifc --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::project_title`
- *RAG Citations:* `inv_ifc::field_guide_01_project_title`

**Financing Window (Sovereign vs. Non-Sovereign / Private Sector)** (`sovereign_window`) — Status: `FILLED` | Confidence: `0.95` | Mode: `HYBRID_KAG_RAG (KAG-primary)`
> Non-Sovereign Operations (NSO) / Private Sector Window (Derived from applicant_type='Large Corporate' against IFC mandate)
- *KAG Trace:* `inv_ifc --[ACCEPTS_APPLICANT]--> applicant::large_corporate => Non-Sovereign Operations (NSO) / Private Sector Window`
- *RAG Citations:* `inv_ifc::field_guide_02_sovereign_window`

### 2. Strategic Alignment

**COP31 Country Platform & Flagship Initiative Alignment** (`cop31_platform_alignment`) — Status: `FILLED` | Confidence: `0.93` | Mode: `HYBRID_KAG_RAG`
> Aligns directly with International Finance Corporation (IFC)'s COP31 Antalya role (Founding private-sector partner of Türkiye Industrial Decarbonization Investment Platform (TIDIP) targeting $6B by 2030) and 2026 commitment (Co-anchoring $6B TIDIP mobilization for steel, aluminum, cement & fertilizer decarbonization plus private-sector climate debt/equity). Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project deploys Industrial Decarbonization in Türkiye, fitting priority sectors (Industrial Decarbonization, Renewable Energy, Energy Storage) via Senior Debt. Grounded in policy references [inv_ifc::field_guide_03_cop31_platform_alignment], [inv_ifc::mandate_cop31].
- *KAG Trace:* `inv_ifc --[ANNOUNCES_AT_COP31]--> cop31::inv_ifc + --[FUNDS_SECTOR]--> Industrial Decarbonization`
- *RAG Citations:* `inv_ifc::field_guide_03_cop31_platform_alignment`, `inv_ifc::mandate_cop31`, `inv_ifc::field_guide_07_ghg_and_adaptation_impact`

### 3. Financial Structuring

**Requested Financing Instrument & Amount (USD)** (`requested_instrument_and_amount`) — Status: `FILLED` | Confidence: `0.94` | Mode: `HYBRID_KAG_RAG (KAG-primary)`
> Instrument: Senior Debt | Requested Amount: $45,000,000 USD | Tenor/Horizon: 4 years | Investor Band: $10,000,000–$250,000,000 (WITHIN BOUNDS)
- *KAG Trace:* `inv_ifc --[OFFERS_INSTRUMENT]--> Senior Debt [bounds: $10,000,000-$250,000,000]`
- *RAG Citations:* `inv_ifc::field_guide_04_requested_instrument_and_amount`

**Total Project Cost & Co-Financing Mobilization Plan** (`cofinancing_structure`) — Status: `FILLED` | Confidence: `0.93` | Mode: `HYBRID_KAG_RAG`
> Total Cost: $95,000,000 | Requested from IFC: $45,000,000 (Senior Debt) | Committed Co-Financing: $30,000,000 (Leverage Ratio: 0.67x) | Remaining Sponsor Equity / Co-Investor Mobilization: $20,000,000. Grounded in policy references [inv_ifc::field_guide_05_cofinancing_structure], [inv_ifc::instruments_tickets].
- *KAG Trace:* `inv_ifc --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::cofinancing_structure`
- *RAG Citations:* `inv_ifc::field_guide_05_cofinancing_structure`, `inv_ifc::instruments_tickets`, `inv_ifc::mandate_cop31`

### 4. Climate & Technical Rationale

**Paris Agreement Alignment Assessment (BB1 Mitigation & BB2 Physical Risk)** (`paris_alignment_bb1_bb2`) — Status: `FILLED` | Confidence: `0.94` | Mode: `HYBRID_KAG_RAG (KAG-primary)`
> ALIGNED (BB1 Mitigation & BB2 Adaptation Verified): Formal Paris Alignment screening completed for Industrial Decarbonization; zero unabated fossil-fuel lock-in; aligned with Türkiye NDC targets.
- *KAG Trace:* `inv_ifc --[REQUIRES_COMPLIANCE]--> Paris_Alignment_BB1_BB2 --[VALIDATES_FIELD]--> field::paris_alignment_bb1_bb2`
- *RAG Citations:* `inv_ifc::field_guide_06_paris_alignment_bb1_bb2`
- *Compliance Notes:* KG Validated Rules: Paris Alignment & GHG emissions accounting

**Quantified Climate Impact (tCO2e/year Avoided &/or Adaptation Beneficiaries)** (`ghg_and_adaptation_impact`) — Status: `FILLED` | Confidence: `0.93` | Mode: `HYBRID_KAG_RAG`
> Quantified Climate Impact: 185,000 tCO2e/year avoided; 1,200 direct adaptation beneficiaries. Cuts steelmaking Scope 1 and Scope 2 carbon intensity by 62% (185,000 tCO2e/year avoided), directly supporting Türkiye's 2035 NDC and TIDIP industrial decarbonization targets. Directly mitigates EU CBAM carbon border liability for Turkish/regional exports. Projected commercial IRR: 15.8%. Grounded in policy references [inv_ifc::field_guide_07_ghg_and_adaptation_impact], [inv_ifc::compliance_esg].
- *KAG Trace:* `inv_ifc --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::ghg_and_adaptation_impact`
- *RAG Citations:* `inv_ifc::field_guide_07_ghg_and_adaptation_impact`, `inv_ifc::compliance_esg`, `inv_ifc::field_guide_03_cop31_platform_alignment`
- *Compliance Notes:* KG Validated Rules: Paris Alignment & GHG emissions accounting

### 5. Safeguards & Governance

**Environmental & Social (E&S) Safeguards & EIA Status** (`es_safeguards_category`) — Status: `FILLED` | Confidence: `0.93` | Mode: `HYBRID_KAG_RAG (KAG-primary)`
> Exclusion Screening: PASS (Zero prohibited fossil-fuel exposure) | E&S / Permits: EIA / ÇED permits obtained | Social/ESG Impact: Creates 320 green engineering jobs, zero coal usage, closed-loop 85% process water recycling, and formal workforce reskilling aligned with Just Transition principles.
- *KAG Trace:* `inv_ifc --[EXCLUDES + REQUIRES_COMPLIANCE]--> field::es_safeguards_category`
- *RAG Citations:* `inv_ifc::field_guide_08_es_safeguards_category`

**Financial Viability & Bankability Indicators (Revenue, EBITDA, IRR)** (`financial_viability_metrics`) — Status: `FILLED` | Confidence: `0.94` | Mode: `HYBRID_KAG_RAG (KAG-primary)`
> Total Project Capex: $95,000,000 | Annual Revenue: $240,000,000 | EBITDA: $42,000,000 | Projected IRR: 15.8%
- *KAG Trace:* `inv_ifc --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::financial_viability_metrics`
- *RAG Citations:* `inv_ifc::field_guide_09_financial_viability_metrics`

### 6. Execution & Risks

**Project Readiness Stage & Implementation Schedule** (`implementation_timeline`) — Status: `FILLED` | Confidence: `0.96` | Mode: `HYBRID_KAG_RAG (KAG-primary)`
> Current Maturity: Ready-to-Build | Expected Implementation Horizon: 4 years
- *KAG Trace:* `inv_ifc --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::implementation_timeline`
- *RAG Citations:* `inv_ifc::field_guide_10_implementation_timeline`

**Key Technical, Market & Climate Risks with Mitigants** (`key_risks_and_mitigants`) — Status: `FILLED` | Confidence: `0.95` | Mode: `HYBRID_KAG_RAG (RAG-primary)`
> Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (Anatolia Clean Metallurgy A.Ş., Türkiye) seeks $45,000,000 under International Finance Corporation (IFC)'s Senior Debt. Retrofitting a major Turkish steel rolling facility to 100% renewable-powered electric-arc furnace operation paired with 120 MW captive solar PV and 60 MWh lithium-iron-phosphate battery storage to achieve EU CBAM compliance. Contact [REDACTED_EMAIL_1] for technical annex. Expected impact: 185,000 tCO2e/year. [inv_ifc::field_guide_11_key_risks_and_mitigants] [inv_ifc::instruments_tickets]
- *KAG Trace:* `inv_ifc --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::key_risks_and_mitigants`
- *RAG Citations:* `inv_ifc::field_guide_11_key_risks_and_mitigants`, `inv_ifc::instruments_tickets`, `inv_ifc::form_standard`

### 7. Executive Summary

**Executive Concept Note Abstract** (`executive_concept_summary`) — Status: `FILLED` | Confidence: `0.93` | Mode: `HYBRID_KAG_RAG`
> Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (Anatolia Clean Metallurgy A.Ş., Türkiye) requests $45,000,000 via IFC's Senior Debt. Retrofitting a major Turkish steel rolling facility to 100% renewable-powered electric-arc furnace operation paired with 120 MW captive solar PV and 60 MWh lithium-iron-phosphate battery storage to achieve EU CBAM compliance. Contact [REDACTED_EMAIL_1] for technical annex. Climate Impact: 185,000 tCO2e/year avoided; 1,200 direct adaptation beneficiaries. Aligned with COP31 Antalya commitment (Co-anchoring $6B TIDIP mobilization for steel, aluminum, cement & fertilizer decarbonization plus private-sector climate debt/equity). Grounded in policy references [inv_ifc::field_guide_12_executive_concept_summary], [inv_ifc::form_standard].
- *KAG Trace:* `inv_ifc --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::executive_concept_summary`
- *RAG Citations:* `inv_ifc::field_guide_12_executive_concept_summary`, `inv_ifc::form_standard`, `inv_ifc::field_guide_07_ghg_and_adaptation_impact`

## Pre-Submission Human & Compliance Checklist

- [ ] [Mandatory Requirement] IFC Performance Standards (PS 1-8) compliance
- [ ] [Mandatory Requirement] Paris Alignment & GHG emissions accounting
- [ ] [Mandatory Requirement] Commercial bankability & audited financials
- [ ] [Mandatory Requirement] Private-sector ownership (>50% private or commercially managed)
- [ ] [Screening Warning] Missing mandatory NDA / Operational Focal Point No-Objection Letter (required before final submission).
- [ ] [Portal Submission] Upload finalized packet via official portal: https://www.ifc.org/en/what-we-do/sector-expertise/climate-business
