# GreenHope × COP31 Antalya (Nov 9–20, 2026) Investor Intelligence, Security & KAG/RAG Platform

An end-to-end, cryptographically secured COP31 investor intelligence system, central KAG + scoped RAG engine, anti-hallucination application-filling agent, and interactive web application built for **GreenHope** and multi-sector climate-finance applicants.

## Key Capabilities

1. **66-Entity Verified COP31 Antalya Database (JSON, CSV, 5-Sheet Excel `.xlsx`)**
   - Combines the 44 verified COP31 banks/MDBs/DFIs/climate funds with the COP31 Business Forum Climate Finance & Investments Working Group V1 institutions, climate-finance networks (GEFI, FAST-Infra, IIAB, GFIF, GGGI, Investment Office of Türkiye), and COP31 Climate Supporters (Siemens, GE Vernova, Cisco, SAP, IKEA).
   - Strictly enforces `relationship_status` governance (`Investor Confirmed`, `Finance Participant`, `Potential Strategic Partner`, `COP31 Supporter`) so sponsors/supporters are never falsely tagged as direct investors.
   - Organizes all entities by **Tier A / Tier B / Tier C** attack sequence and **P1 / P2 / P3** AI/RAG build priority.

2. **Step 1 Cryptographic Vault & 4-Tier IP Protection (`src/security/`)**
   - `AES-256-GCM` encryption at rest + `PBKDF2-HMAC-SHA256` (600,000 iterations) + `HKDF-SHA256` per-investor tenant isolation + SHA-256 Merkle Root + HMAC-SHA256 manifest + RBAC + tamper-evident SHA-256 hash-chained `audit_log.jsonl`.
   - **4-Tier Anti-Copying IP Classification** (`LEVEL_1_PUBLIC`, `LEVEL_2_INTERNAL`, `LEVEL_3_CONFIDENTIAL`, `LEVEL_4_RESTRICTED`): proprietary algorithms, unpublished patent claims, and secrets are permanently blocked from auto-submission.

3. **Central Canonical Architecture (`GREENHOPE_MASTER` + Central KAG + Central Scoped RAG)**
   - `data/greenhope_master.json`: Canonical Single Source of Truth for GreenHope (`GreenHope → city pilot → measurable climate impact → financing → scale`).
   - `investors/<slug>/`: **First 10 Verified P1 Investor Knowledge Packs** (`bbva`, `garanti_bbva`, `aiib`, `world_bank`, `qnb`, `meridiam`, `m_and_g`, `hsbc`, `akbank`, `denizbank`) — 13 structured files each including `application_questions.json` and `evidence/verified_claims.json`.
   - `src/models/greenhope_kag_rag.py`: Unified Central Knowledge Graph (7 GreenHope domains ↔ 66 COP31 entities), Central Scoped RAG engine, evidence-backed Investor Comparator (e.g., BBVA vs. Ziraat Bankası), and Zero-Hallucination Application-Filling Agent (`AUTO-FILL → REVIEW → APPROVE → SUBMIT`).
   - `investor_models/<investor_id>/`: 66 isolated per-investor KAG / RAG / Hybrid model artifacts.

4. **Live Web Application (`webapp/server.py`)**
   - One-Click **Demo Login** + RBAC role quick-enter + credentials login (`demo` / `cop31demo`).
   - Direct **Download Project ZIP** (`/api/download/project.zip`) and **Excel Registry** (`/api/download/excel`) buttons.

## Quick Start

```bash
# 1. Run the complete pipeline (builds 66-entity Excel/JSON/CSV, 10 Knowledge Packs, Vault, 66 Models & Project ZIP)
python3 scripts/run_full_pipeline.py

# 2. Run the automated security, KAG/RAG, IP-guard & zero-hallucination test suite
pytest -v tests/test_cop31_system.py

# 3. Launch the interactive web platform (http://0.0.0.0:8080)
python3 webapp/server.py
```
