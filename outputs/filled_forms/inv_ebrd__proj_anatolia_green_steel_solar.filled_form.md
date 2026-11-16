# Auto-Filled COP31 Investor Application Packet

- **Submission ID:** `sub_inv_ebrd_proj_anatolia_green_steel_solar_1a98913a`
- **Target Investor / Bank:** European Bank for Reconstruction and Development (EBRD) (`inv_ebrd`)
- **AI Model Architecture:** `KAG`
- **Form Template:** Multilateral Development Bank (MDB) Climate Project Concept Note (`MDB_CONCEPT_NOTE`)
- **Applicant Project:** Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (`proj_anatolia_green_steel_solar`)
- **Security Controls:** Tenant Isolation Verified=`True` | PII Redacted=`True`
- **Eligibility Decision:** `ELIGIBLE` (Fit Score: **100.0/100**, Recommended Instrument: **Senior Debt**)
- **Completion Rate:** **100.0%** | **Average Confidence:** **0.93**
- **Synthesis Backend:** `deterministic-grounded-synthesizer-v1`

## Eligibility Screening Summary

- [PASS] Applicant type 'Large Corporate' matched via ACCEPTS_APPLICANT (Large Corporate, Project SPV, Municipality, Financial Intermediary, SME).
- [PASS] Geography 'Türkiye (EMEA)' covered via COVERS_REGION (Türkiye, Europe, Central Asia, MENA, Sub-Saharan Africa, Emerging Markets).
- [PASS] Sector alignment verified via FUNDS_SECTOR: Industrial Decarbonization, Renewable Energy.
- [PASS] Requested ticket $45,000,000 fits within bounds ($5,000,000–$300,000,000).
- [PASS] Instrument match via OFFERS_INSTRUMENT: 'Senior Debt'.
- [PASS] Exclusion list screening passed (no prohibited coal/unabated fossil-fuel activities).
- [PASS] No hard pre-submission compliance blockers detected in REQUIRES_COMPLIANCE graph.

## Auto-Filled Form Fields

### 1. Identification

**Project Title & Legal Sponsor** (`project_title`) — Status: `FILLED` | Confidence: `0.98` | Mode: `KAG`
> Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project | Sponsor: Anatolia Clean Metallurgy A.Ş. (Large Corporate) | Jurisdiction: Türkiye (EMEA) | Primary Sector: Industrial Decarbonization
- *KAG Trace:* `inv_ebrd --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::project_title`

**Financing Window (Sovereign vs. Non-Sovereign / Private Sector)** (`sovereign_window`) — Status: `FILLED` | Confidence: `0.95` | Mode: `KAG`
> Non-Sovereign Operations (NSO) / Private Sector Window (Derived from applicant_type='Large Corporate' against EBRD mandate)
- *KAG Trace:* `inv_ebrd --[ACCEPTS_APPLICANT]--> applicant::large_corporate => Non-Sovereign Operations (NSO) / Private Sector Window`

### 2. Strategic Alignment

**COP31 Country Platform & Flagship Initiative Alignment** (`cop31_platform_alignment`) — Status: `FILLED` | Confidence: `0.90` | Mode: `KAG`
> Aligns directly with European Bank for Reconstruction and Development (EBRD)'s COP31 Antalya role (Co-host of COP31 Global Finance Summit; Joint MDB Pavilion; TIDIP partner; Electrify Now Finance Coalition; GEFF Türkiye) and 2026 commitment (Green Economy Transition (GET) Strategy 2026–2030; €26B+ cumulative commitments in Türkiye; TIDIP & Kazakhstan JETP partner). Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project deploys Industrial Decarbonization in Türkiye, fitting priority sectors (Renewable Energy, Electrification & Grid, Industrial Decarbonization) via Senior Debt.
- *KAG Trace:* `inv_ebrd --[ANNOUNCES_AT_COP31]--> cop31::inv_ebrd + --[FUNDS_SECTOR]--> Industrial Decarbonization`

### 3. Financial Structuring

**Requested Financing Instrument & Amount (USD)** (`requested_instrument_and_amount`) — Status: `FILLED` | Confidence: `0.94` | Mode: `KAG`
> Instrument: Senior Debt | Requested Amount: $45,000,000 USD | Tenor/Horizon: 4 years | Investor Band: $5,000,000–$300,000,000 (WITHIN BOUNDS)
- *KAG Trace:* `inv_ebrd --[OFFERS_INSTRUMENT]--> Senior Debt [bounds: $5,000,000-$300,000,000]`

**Total Project Cost & Co-Financing Mobilization Plan** (`cofinancing_structure`) — Status: `FILLED` | Confidence: `0.90` | Mode: `KAG`
> Total Cost: $95,000,000 | Requested from EBRD: $45,000,000 (Senior Debt) | Committed Co-Financing: $30,000,000 (Leverage Ratio: 0.67x) | Remaining Sponsor Equity / Co-Investor Mobilization: $20,000,000.
- *KAG Trace:* `inv_ebrd --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::cofinancing_structure`

### 4. Climate & Technical Rationale

**Paris Agreement Alignment Assessment (BB1 Mitigation & BB2 Physical Risk)** (`paris_alignment_bb1_bb2`) — Status: `FILLED` | Confidence: `0.94` | Mode: `KAG`
> ALIGNED (BB1 Mitigation & BB2 Adaptation Verified): Formal Paris Alignment screening completed for Industrial Decarbonization; zero unabated fossil-fuel lock-in; aligned with Türkiye NDC targets.
- *KAG Trace:* `inv_ebrd --[REQUIRES_COMPLIANCE]--> Paris_Alignment_BB1_BB2 --[VALIDATES_FIELD]--> field::paris_alignment_bb1_bb2`
- *Compliance Notes:* KG Validated Rules: EBRD Green Economy Transition (GET) & Paris Alignment assessment

**Quantified Climate Impact (tCO2e/year Avoided &/or Adaptation Beneficiaries)** (`ghg_and_adaptation_impact`) — Status: `FILLED` | Confidence: `0.90` | Mode: `KAG`
> Quantified Climate Impact: 185,000 tCO2e/year avoided; 1,200 direct adaptation beneficiaries. Cuts steelmaking Scope 1 and Scope 2 carbon intensity by 62% (185,000 tCO2e/year avoided), directly supporting Türkiye's 2035 NDC and TIDIP industrial decarbonization targets. Directly mitigates EU CBAM carbon border liability for Turkish/regional exports. Projected commercial IRR: 15.8%.
- *KAG Trace:* `inv_ebrd --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::ghg_and_adaptation_impact`

### 5. Safeguards & Governance

**Environmental & Social (E&S) Safeguards & EIA Status** (`es_safeguards_category`) — Status: `FILLED` | Confidence: `0.93` | Mode: `KAG`
> Exclusion Screening: PASS (Zero prohibited fossil-fuel exposure) | E&S / Permits: EIA / ÇED permits obtained | Social/ESG Impact: Creates 320 green engineering jobs, zero coal usage, closed-loop 85% process water recycling, and formal workforce reskilling aligned with Just Transition principles.
- *KAG Trace:* `inv_ebrd --[EXCLUDES + REQUIRES_COMPLIANCE]--> field::es_safeguards_category`
- *Compliance Notes:* KG Validated Rules: EBRD Environmental and Social Policy (PR 1-10) & EIA permits

**Financial Viability & Bankability Indicators (Revenue, EBITDA, IRR)** (`financial_viability_metrics`) — Status: `FILLED` | Confidence: `0.94` | Mode: `KAG`
> Total Project Capex: $95,000,000 | Annual Revenue: $240,000,000 | EBITDA: $42,000,000 | Projected IRR: 15.8%
- *KAG Trace:* `inv_ebrd --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::financial_viability_metrics`

### 6. Execution & Risks

**Project Readiness Stage & Implementation Schedule** (`implementation_timeline`) — Status: `FILLED` | Confidence: `0.96` | Mode: `KAG`
> Current Maturity: Ready-to-Build | Expected Implementation Horizon: 4 years
- *KAG Trace:* `inv_ebrd --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::implementation_timeline`

**Key Technical, Market & Climate Risks with Mitigants** (`key_risks_and_mitigants`) — Status: `FILLED` | Confidence: `0.90` | Mode: `KAG`
> Grid curtailment risk mitigated via 60 MWh BESS; FX mismatch mitigated by EUR-denominated EU green-steel export offtake contracts covering 75% of output; EPC turnkey fixed-price contract. Supported by EBRD risk-sharing instruments (Senior Debt, Equity, Subordinated Debt).
- *KAG Trace:* `inv_ebrd --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::key_risks_and_mitigants`

### 7. Executive Summary

**Executive Concept Note Abstract** (`executive_concept_summary`) — Status: `FILLED` | Confidence: `0.90` | Mode: `KAG`
> Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (Anatolia Clean Metallurgy A.Ş., Türkiye) requests $45,000,000 via EBRD's Senior Debt. Retrofitting a major Turkish steel rolling facility to 100% renewable-powered electric-arc furnace operation paired with 120 MW captive solar PV and 60 MWh lithium-iron-phosphate battery storage to achieve EU CBAM compliance. Contact [REDACTED_EMAIL_1] for technical annex. Climate Impact: 185,000 tCO2e/year avoided; 1,200 direct adaptation beneficiaries. Aligned with COP31 Antalya commitment (Green Economy Transition (GET) Strategy 2026–2030; €26B+ cumulative commitments in Türkiye; TIDIP & Kazakhstan JETP partner).
- *KAG Trace:* `inv_ebrd --[USES_FORM_TEMPLATE]--> form::MDB_CONCEPT_NOTE --[HAS_FORM_FIELD]--> field::executive_concept_summary`

## Pre-Submission Human & Compliance Checklist

- [ ] [Mandatory Requirement] EBRD Green Economy Transition (GET) & Paris Alignment assessment
- [ ] [Mandatory Requirement] EBRD Environmental and Social Policy (PR 1-10) & EIA permits
- [ ] [Mandatory Requirement] Sound banking principles & transition impact demonstration
- [ ] [Mandatory Requirement] Integrity & KYC beneficial ownership disclosure
- [ ] [Portal Submission] Upload finalized packet via official portal: https://www.ebrd.com/work-with-us/project-finance.html
