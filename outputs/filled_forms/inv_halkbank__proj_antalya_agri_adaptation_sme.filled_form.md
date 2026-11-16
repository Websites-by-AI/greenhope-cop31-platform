# Auto-Filled COP31 Investor Application Packet

- **Submission ID:** `sub_inv_halkbank_proj_antalya_agri_adaptation_sme_9406d967`
- **Target Investor / Bank:** Halkbank (`inv_halkbank`)
- **AI Model Architecture:** `RAG`
- **Form Template:** Turkish Commercial / State Bank Sustainable & Green Transformation Loan Application (`TURKISH_BANK_GREEN_LOAN`)
- **Applicant Project:** Antalya Solar-Powered Precision Drip Irrigation & Climate-Resilient Cold Chain (`proj_antalya_agri_adaptation_sme`)
- **Security Controls:** Tenant Isolation Verified=`True` | PII Redacted=`True`
- **Eligibility Decision:** `ELIGIBLE` (Fit Score: **99.2/100**, Recommended Instrument: **KGF-Backed Green Loan**)
- **Completion Rate:** **100.0%** | **Average Confidence:** **0.95**
- **Synthesis Backend:** `deterministic-grounded-synthesizer-v1`

## Eligibility Screening Summary

- [PASS] Retrieved mandate confirms coverage for Türkiye (Türkiye).
- [PASS] Applicant profile 'SME' aligns with Halkbank banking segment.
- [PASS] Ticket $1,800,000 fits Halkbank band ($25,000–$50,000,000).
- [PASS] No fossil-fuel exclusion conflicts found.
- [PASS] Matched financing product 'KGF-Backed Green Loan'.

## Auto-Filled Form Fields

### 1. Applicant Identification

**Company Legal Name & Masked Tax ID (VKN)** (`company_identity_masked`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Akdeniz Yeşil Tarım Kooperatifi Ltd. | Masked VKN/Tax ID: VK********6281 | Jurisdiction: Türkiye
- *RAG Citations:* `inv_halkbank::field_guide_01_company_identity_masked`, `inv_halkbank::sectors_geography`, `inv_halkbank::compliance_esg`
- *Compliance Notes:* PII masked via PIIRedactor during RAG processing.

**Enterprise Segment (SME / Mid-Cap / Corporate / Exporter)** (`enterprise_segment`) — Status: `FILLED` | Confidence: `0.94` | Mode: `RAG`
> SME (EU CBAM Exporter)
- *RAG Citations:* `inv_halkbank::field_guide_02_enterprise_segment`, `inv_halkbank::instruments_tickets`, `inv_halkbank::compliance_esg`

### 2. Product Selection

**Selected COP31 Green Financing Package / Credit Line** (`bank_green_program`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Target Program: Halkbank — Official COP31 Main Partner; launched dedicated COP31 TRY 100B SME Sustainability Transformation Package (31 products). COP31 2026 Commitment: TRY 100 billion COP31 SME Sustainability Transformation Package (31 green/social credit products, partly KGF-backed; TRY 424B cumulative green/social contribution). Recommended Facility: KGF-Backed Green Loan aligned with Sustainable Agriculture & Water. [inv_halkbank::field_guide_03_bank_green_program] [inv_halkbank::form_standard]
- *RAG Citations:* `inv_halkbank::field_guide_03_bank_green_program`, `inv_halkbank::form_standard`, `inv_halkbank::field_guide_06_carbon_and_cbam_impact`

**Requested Financing Amount (USD eq.) & Tenor** (`loan_amount_and_maturity`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> KGF-Backed Green Loan | Requested: $1,800,000 USD | Maturity: 3 years | Program Range: $25,000–$50,000,000 (In Range). [inv_halkbank::field_guide_04_loan_amount_and_maturity] [inv_halkbank::instruments_tickets]
- *RAG Citations:* `inv_halkbank::field_guide_04_loan_amount_and_maturity`, `inv_halkbank::instruments_tickets`, `inv_halkbank::sectors_geography`

### 3. Green Technical Criteria

**Eligible Green Use of Proceeds & Technology Description** (`eligible_green_use_of_proceeds`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Green Use of Proceeds (Sustainable Agriculture & Water): LoRaWAN soil-moisture & evapotranspiration sensors automated with solar pumping and natural-refrigerant cold chain extending export shelf life by 40%. Maps to Halkbank eligible categories (SME Green Transition, Renewable Energy, Energy Efficiency) and governing requirements (Turkish SME / tradesperson / corporate registration (VKN & KOSGEB/KOBİ status); Selection among 31 eligible green/social transformation credit categories). [inv_halkbank::field_guide_05_eligible_green_use_of_proceeds] [inv_halkbank::sectors_geography]
- *RAG Citations:* `inv_halkbank::field_guide_05_eligible_green_use_of_proceeds`, `inv_halkbank::sectors_geography`, `inv_halkbank::compliance_esg`

**Carbon Footprint Reduction (tCO2e/yr) & EU CBAM Export Impact** (`carbon_and_cbam_impact`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Projected Emissions Reduction: 4,200 tCO2e/year. Addresses severe Mediterranean drought and extreme heat risks by reducing groundwater extraction by 4.1 million m3/year while replacing diesel irrigation pumps with solar PV (4,200 tCO2e/year avoided). Directly reduces EU CBAM carbon border exposure for export supply chains. Aligned with Halkbank sustainable finance KPI reporting. [inv_halkbank::field_guide_06_carbon_and_cbam_impact] [inv_halkbank::sectors_geography]
- *RAG Citations:* `inv_halkbank::field_guide_06_carbon_and_cbam_impact`, `inv_halkbank::sectors_geography`, `inv_halkbank::form_standard`

### 4. Credit & Collateral

**Collateral / Kredi Garanti Fonu (KGF) Guarantee Eligibility** (`collateral_and_kgf_status`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Collateral / KGF Guarantee Available for Halkbank green credit line underwriting. [inv_halkbank::field_guide_07_collateral_and_kgf_status] [inv_halkbank::compliance_esg]
- *RAG Citations:* `inv_halkbank::field_guide_07_collateral_and_kgf_status`, `inv_halkbank::compliance_esg`, `inv_halkbank::sectors_geography`

**Inclusive Finance Eligibility (Women/Youth Entrepreneur / Regional Priority)** (`inclusive_priority_flags`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Women/Youth Entrepreneur Preferential Window | EU CBAM Green Export Priority. [inv_halkbank::field_guide_08_inclusive_priority_flags] [inv_halkbank::instruments_tickets]
- *RAG Citations:* `inv_halkbank::field_guide_08_inclusive_priority_flags`, `inv_halkbank::instruments_tickets`, `inv_halkbank::sectors_geography`

**Financial Performance Snapshot (Annual Revenue, EBITDA, Project Capex)** (`financial_snapshot`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Capex: $2,600,000 | Revenue: $6,400,000 | EBITDA: $1,150,000 | Projected IRR: 18.4%
- *RAG Citations:* `inv_halkbank::field_guide_09_financial_snapshot`, `inv_halkbank::sectors_geography`, `inv_halkbank::instruments_tickets`

### 5. Compliance

**Environmental Permits (ÇED / EIA) & Vendor Green Certification** (`environmental_permits_status`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Exclusion Check: PASS (zero fossil-fuel involvement) | Permits: EIA / ÇED permits confirmed | ESG Summary: Women-owned enterprise employing 68% female agricultural technicians; directly strengthens climate resilience for 14,500 rural residents and 420 smallholder farms. [inv_halkbank::field_guide_10_environmental_permits_status] [inv_halkbank::compliance_esg]
- *RAG Citations:* `inv_halkbank::field_guide_10_environmental_permits_status`, `inv_halkbank::compliance_esg`, `inv_halkbank::sectors_geography`

### 6. Summary

**Relationship Manager Executive Credit & Sustainability Note** (`application_executive_note`) — Status: `FILLED` | Confidence: `0.95` | Mode: `RAG`
> Antalya Solar-Powered Precision Drip Irrigation & Climate-Resilient Cold Chain (Akdeniz Yeşil Tarım Kooperatifi Ltd., Türkiye) seeks $1,800,000 under Halkbank's KGF-Backed Green Loan. Women-led Mediterranean agricultural SME deploying IoT soil-moisture precision drip irrigation across 1,800 hectares in Antalya alongside 2.5 MW agrivoltaic rooftop solar and low-GWP cold storage to cut water consumption by 48%. Expected impact: 4,200 tCO2e/year. [inv_halkbank::field_guide_11_application_executive_note] [inv_halkbank::sectors_geography]
- *RAG Citations:* `inv_halkbank::field_guide_11_application_executive_note`, `inv_halkbank::sectors_geography`, `inv_halkbank::mandate_cop31`

## Pre-Submission Human & Compliance Checklist

- [ ] [Mandatory Requirement] Turkish SME / tradesperson / corporate registration (VKN & KOSGEB/KOBİ status)
- [ ] [Mandatory Requirement] Selection among 31 eligible green/social transformation credit categories
- [ ] [Mandatory Requirement] KGF guarantee or collateral documentation
- [ ] [Mandatory Requirement] Environmental permit & vendor invoice/proforma for green equipment
- [ ] [Portal Submission] Upload finalized packet via official portal: https://www.halkbank.com.tr/en/sustainability.html
