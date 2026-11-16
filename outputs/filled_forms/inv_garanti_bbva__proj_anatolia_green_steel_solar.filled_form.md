# Auto-Filled COP31 Investor Application Packet

- **Submission ID:** `sub_inv_garanti_bbva_proj_anatolia_green_steel_solar_8d64785a`
- **Target Investor / Bank:** Garanti BBVA (`inv_garanti_bbva`)
- **AI Model Architecture:** `RAG`
- **Form Template:** Turkish Commercial / State Bank Sustainable & Green Transformation Loan Application (`TURKISH_BANK_GREEN_LOAN`)
- **Applicant Project:** Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (`proj_anatolia_green_steel_solar`)
- **Security Controls:** Tenant Isolation Verified=`True` | PII Redacted=`True`
- **Eligibility Decision:** `ELIGIBLE` (Fit Score: **97.6/100**, Recommended Instrument: **Green Investment Loan**)
- **Completion Rate:** **100.0%** | **Average Confidence:** **0.95**
- **Synthesis Backend:** `deterministic-grounded-synthesizer-v1`

## Eligibility Screening Summary

- [PASS] Retrieved mandate confirms coverage for Türkiye (Türkiye, EMEA).
- [PASS] Applicant profile 'Large Corporate' aligns with Garanti BBVA banking segment.
- [PASS] Ticket $45,000,000 fits Garanti BBVA band ($100,000–$150,000,000).
- [PASS] No fossil-fuel exclusion conflicts found.
- [PASS] Matched financing product 'Green Investment Loan'.

## Auto-Filled Form Fields

### 1. Applicant Identification

**Company Legal Name & Masked Tax ID (VKN)** (`company_identity_masked`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Anatolia Clean Metallurgy A.Ş. | Masked VKN/Tax ID: VK********3847 | Jurisdiction: Türkiye
- *RAG Citations:* `inv_garanti_bbva::field_guide_01_company_identity_masked`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::compliance_esg`
- *Compliance Notes:* PII masked via PIIRedactor during RAG processing.

**Enterprise Segment (SME / Mid-Cap / Corporate / Exporter)** (`enterprise_segment`) — Status: `FILLED` | Confidence: `0.94` | Mode: `RAG`
> Large Corporate (EU CBAM Exporter)
- *RAG Citations:* `inv_garanti_bbva::field_guide_02_enterprise_segment`, `inv_garanti_bbva::instruments_tickets`, `inv_garanti_bbva::sectors_geography`

### 2. Product Selection

**Selected COP31 Green Financing Package / Credit Line** (`bank_green_program`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Target Program: Garanti BBVA — Official Global Banking Partner of COP31 Antalya (with BBVA Group); 60+ Green Zone Climate Finance Hub sessions; EV/TOGG mobility showcase. COP31 2026 Commitment: TRY 3.5 trillion sustainable finance commitment (2018–2029; >TRY 1 trillion surpassed by Jan 2026) for green transition, renewables, e-mobility & SMEs. Recommended Facility: Green Investment Loan aligned with Industrial Decarbonization. [inv_garanti_bbva::field_guide_03_bank_green_program] [inv_garanti_bbva::sectors_geography]
- *RAG Citations:* `inv_garanti_bbva::field_guide_03_bank_green_program`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::instruments_tickets`

**Requested Financing Amount (USD eq.) & Tenor** (`loan_amount_and_maturity`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Green Investment Loan | Requested: $45,000,000 USD | Maturity: 4 years | Program Range: $100,000–$150,000,000 (In Range). [inv_garanti_bbva::field_guide_04_loan_amount_and_maturity] [inv_garanti_bbva::instruments_tickets]
- *RAG Citations:* `inv_garanti_bbva::field_guide_04_loan_amount_and_maturity`, `inv_garanti_bbva::instruments_tickets`, `inv_garanti_bbva::sectors_geography`

### 3. Green Technical Criteria

**Eligible Green Use of Proceeds & Technology Description** (`eligible_green_use_of_proceeds`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Green Use of Proceeds (Industrial Decarbonization): High-efficiency scrap preheating electric-arc furnace integrated with grid-forming 60 MWh BESS, digital twin energy dispatch, and ISO 14064 real-time carbon MRV. Maps to Garanti BBVA eligible categories (Renewable Energy, Clean Transport & EV, Industrial Decarbonization) and governing requirements (Turkish company registration (VKN) & audited financials; Garanti BBVA Sustainable Finance Framework eligibility). [inv_garanti_bbva::field_guide_05_eligible_green_use_of_proceeds] [inv_garanti_bbva::sectors_geography]
- *RAG Citations:* `inv_garanti_bbva::field_guide_05_eligible_green_use_of_proceeds`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::instruments_tickets`

**Carbon Footprint Reduction (tCO2e/yr) & EU CBAM Export Impact** (`carbon_and_cbam_impact`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Projected Emissions Reduction: 185,000 tCO2e/year. Cuts steelmaking Scope 1 and Scope 2 carbon intensity by 62% (185,000 tCO2e/year avoided), directly supporting Türkiye's 2035 NDC and TIDIP industrial decarbonization targets. Directly reduces EU CBAM carbon border exposure for export supply chains. Aligned with Garanti BBVA sustainable finance KPI reporting. [inv_garanti_bbva::field_guide_06_carbon_and_cbam_impact] [inv_garanti_bbva::sectors_geography]
- *RAG Citations:* `inv_garanti_bbva::field_guide_06_carbon_and_cbam_impact`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::instruments_tickets`

### 4. Credit & Collateral

**Collateral / Kredi Garanti Fonu (KGF) Guarantee Eligibility** (`collateral_and_kgf_status`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Collateral / KGF Guarantee Available for Garanti BBVA green credit line underwriting. [inv_garanti_bbva::field_guide_07_collateral_and_kgf_status] [inv_garanti_bbva::sectors_geography]
- *RAG Citations:* `inv_garanti_bbva::field_guide_07_collateral_and_kgf_status`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::compliance_esg`

**Inclusive Finance Eligibility (Women/Youth Entrepreneur / Regional Priority)** (`inclusive_priority_flags`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> EU CBAM Green Export Priority. [inv_garanti_bbva::field_guide_08_inclusive_priority_flags] [inv_garanti_bbva::sectors_geography]
- *RAG Citations:* `inv_garanti_bbva::field_guide_08_inclusive_priority_flags`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::instruments_tickets`

**Financial Performance Snapshot (Annual Revenue, EBITDA, Project Capex)** (`financial_snapshot`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Capex: $95,000,000 | Revenue: $240,000,000 | EBITDA: $42,000,000 | Projected IRR: 15.8%
- *RAG Citations:* `inv_garanti_bbva::field_guide_09_financial_snapshot`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::instruments_tickets`

### 5. Compliance

**Environmental Permits (ÇED / EIA) & Vendor Green Certification** (`environmental_permits_status`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Exclusion Check: PASS (zero fossil-fuel involvement) | Permits: EIA / ÇED permits confirmed | ESG Summary: Creates 320 green engineering jobs, zero coal usage, closed-loop 85% process water recycling, and formal workforce reskilling aligned with Just Transition principles. [inv_garanti_bbva::field_guide_10_environmental_permits_status] [inv_garanti_bbva::compliance_esg]
- *RAG Citations:* `inv_garanti_bbva::field_guide_10_environmental_permits_status`, `inv_garanti_bbva::compliance_esg`, `inv_garanti_bbva::sectors_geography`

### 6. Summary

**Relationship Manager Executive Credit & Sustainability Note** (`application_executive_note`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Anatolia Green Electric-Arc Steel & 120 MW Solar + BESS Decarbonization Project (Anatolia Clean Metallurgy A.Ş., Türkiye) seeks $45,000,000 under Garanti BBVA's Green Investment Loan. Retrofitting a major Turkish steel rolling facility to 100% renewable-powered electric-arc furnace operation paired with 120 MW captive solar PV and 60 MWh lithium-iron-phosphate battery storage to achieve EU CBAM compliance. Contact [REDACTED_EMAIL_1] for technical annex. Expected impact: 185,000 tCO2e/year. [inv_garanti_bbva::field_guide_11_application_executive_note] [inv_garanti_bbva::sectors_geography]
- *RAG Citations:* `inv_garanti_bbva::field_guide_11_application_executive_note`, `inv_garanti_bbva::sectors_geography`, `inv_garanti_bbva::instruments_tickets`

## Pre-Submission Human & Compliance Checklist

- [ ] [Mandatory Requirement] Turkish company registration (VKN) & audited financials
- [ ] [Mandatory Requirement] Garanti BBVA Sustainable Finance Framework eligibility
- [ ] [Mandatory Requirement] Environmental permits (ÇED/EIA) & energy/carbon savings verification
- [ ] [Mandatory Requirement] Collateral / creditworthiness or KGF guarantee package
- [ ] [Portal Submission] Upload finalized packet via official portal: https://www.garantibbva.com.tr/en/sustainability
