# Auto-Filled COP31 Investor Application Packet

- **Submission ID:** `sub_inv_bbva_group_proj_anatolia_green_steel_solar_1a8c2012`
- **Target Investor / Bank:** BBVA Group (`inv_bbva_group`)
- **AI Model Architecture:** `RAG`
- **Form Template:** Global Corporate & Investment Bank Green / Sustainability-Linked Finance Mandate Intake (`GLOBAL_COMMERCIAL_BANK_TRANSITION`)
- **Applicant Project:** Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (`proj_anatolia_green_steel_solar`)
- **Security Controls:** Tenant Isolation Verified=`True` | PII Redacted=`True`
- **Eligibility Decision:** `ELIGIBLE` (Fit Score: **78.8/100**, Recommended Instrument: **Green Loan**)
- **Completion Rate:** **100.0%** | **Average Confidence:** **0.95**
- **Synthesis Backend:** `deterministic-grounded-synthesizer-v1`

## Eligibility Screening Summary

- [PASS] Retrieved mandate confirms coverage for Türkiye (Global, Europe, Türkiye).
- [PASS] Applicant profile 'Large Corporate' aligns with BBVA banking segment.
- [PASS] Ticket $45,000,000 fits BBVA band ($5,000,000–$500,000,000).
- [PASS] No fossil-fuel exclusion conflicts found.

## Auto-Filled Form Fields

### 1. Borrower Overview

**Corporate Borrower & Operating Jurisdiction** (`borrower_profile`) — Status: `FILLED` | Confidence: `0.97` | Mode: `RAG`
> Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project | Entity: Anatolia Clean Metallurgy A.Ş. (Large Corporate) | Market: Türkiye | Sector: Industrial Decarbonization
- *RAG Citations:* `inv_bbva_group::field_guide_01_borrower_profile`, `inv_bbva_group::sectors_geography`, `inv_bbva_group::instruments_tickets`

### 2. Structuring

**Recommended Sustainable Finance Structure (Green Loan / SLL / Green Bond / Trade Finance)** (`facility_structure`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Green Loan | Requested: $45,000,000 USD | Maturity: 4 years | Program Range: $5,000,000–$500,000,000 (In Range). [inv_bbva_group::field_guide_02_facility_structure] [inv_bbva_group::instruments_tickets]
- *RAG Citations:* `inv_bbva_group::field_guide_02_facility_structure`, `inv_bbva_group::instruments_tickets`, `inv_bbva_group::form_standard`

**Taxonomy & Market Standards Alignment (EU Taxonomy / ICMA GBP / LMA GLP)** (`taxonomy_alignment`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Green Use of Proceeds (Industrial Decarbonization): High-efficiency scrap preheating electric-arc furnace integrated with grid-forming 60 MWh BESS, digital twin energy dispatch, and ISO 14064 real-time carbon MRV. Maps to BBVA eligible categories (Electrification & Grid, Renewable Energy, Climate-Tech Innovation) and governing requirements (LMA Green Loan Principles / Sustainability-Linked Loan Principles / ICMA GBP alignment; EU Taxonomy or BBVA Sustainable Finance Framework eligibility). [inv_bbva_group::field_guide_03_taxonomy_alignment] [inv_bbva_group::compliance_esg]
- *RAG Citations:* `inv_bbva_group::field_guide_03_taxonomy_alignment`, `inv_bbva_group::compliance_esg`, `inv_bbva_group::sectors_geography`

### 3. Transition Credibility

**Proposed Sustainability Performance Targets (SPTs) & Decarbonization KPIs** (`spts_and_kpis`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Projected Emissions Reduction: 185,000 tCO2e/year. Cuts steelmaking Scope 1 and Scope 2 carbon intensity by 62% (185,000 tCO2e/year avoided), directly supporting Türkiye's 2035 NDC and TIDIP industrial decarbonization targets. Directly reduces EU CBAM carbon border exposure for export supply chains. Aligned with BBVA sustainable finance KPI reporting. [inv_bbva_group::field_guide_04_spts_and_kpis] [inv_bbva_group::sectors_geography]
- *RAG Citations:* `inv_bbva_group::field_guide_04_spts_and_kpis`, `inv_bbva_group::sectors_geography`, `inv_bbva_group::compliance_esg`

**Second-Party Opinion (SPO) & Independent Assurance Readiness** (`spo_and_verification`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Second-Party Opinion (SPO) & independent GHG assurance ready for BBVA sustainable finance labeling. [inv_bbva_group::field_guide_05_spo_and_verification] [inv_bbva_group::sectors_geography]
- *RAG Citations:* `inv_bbva_group::field_guide_05_spo_and_verification`, `inv_bbva_group::sectors_geography`, `inv_bbva_group::compliance_esg`

### 4. Risk & Underwriting

**Sector Exclusion & ESG Risk Screening** (`esg_controversy_screen`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Exclusion Check: PASS (zero fossil-fuel involvement) | Permits: EIA / ÇED permits confirmed | ESG Summary: Creates 320 green engineering jobs, zero coal usage, closed-loop 85% process water recycling, and formal workforce reskilling aligned with Just Transition principles. [inv_bbva_group::field_guide_06_esg_controversy_screen] [inv_bbva_group::sectors_geography]
- *RAG Citations:* `inv_bbva_group::field_guide_06_esg_controversy_screen`, `inv_bbva_group::sectors_geography`, `inv_bbva_group::compliance_esg`

**Credit Profile (Revenue, EBITDA, Capex, Expected IRR)** (`credit_financials`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Capex: $95,000,000 | Revenue: $240,000,000 | EBITDA: $42,000,000 | Projected IRR: 15.8%
- *RAG Citations:* `inv_bbva_group::field_guide_07_credit_financials`, `inv_bbva_group::instruments_tickets`, `inv_bbva_group::sectors_geography`

### 5. Mandate Pitch

**Detailed Use of Proceeds & Transition Plan Summary** (`use_of_proceeds_narrative`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Green Use of Proceeds (Industrial Decarbonization): High-efficiency scrap preheating electric-arc furnace integrated with grid-forming 60 MWh BESS, digital twin energy dispatch, and ISO 14064 real-time carbon MRV. Maps to BBVA eligible categories (Electrification & Grid, Renewable Energy, Climate-Tech Innovation) and governing requirements (LMA Green Loan Principles / Sustainability-Linked Loan Principles / ICMA GBP alignment; EU Taxonomy or BBVA Sustainable Finance Framework eligibility). [inv_bbva_group::field_guide_08_use_of_proceeds_narrative] [inv_bbva_group::sectors_geography]
- *RAG Citations:* `inv_bbva_group::field_guide_08_use_of_proceeds_narrative`, `inv_bbva_group::sectors_geography`, `inv_bbva_group::compliance_esg`

## Pre-Submission Human & Compliance Checklist

- [ ] [Mandatory Requirement] LMA Green Loan Principles / Sustainability-Linked Loan Principles / ICMA GBP alignment
- [ ] [Mandatory Requirement] EU Taxonomy or BBVA Sustainable Finance Framework eligibility
- [ ] [Mandatory Requirement] Scope 1/2/3 decarbonization KPIs & transition plan
- [ ] [Mandatory Requirement] Credit underwriting & Second-Party Opinion (for labeled bonds/SLLs)
- [ ] [Portal Submission] Upload finalized packet via official portal: https://www.bbva.com/en/sustainability/
