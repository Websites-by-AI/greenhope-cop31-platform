"""End-to-end orchestrator running:
  Stage 0: Build 66-entity COP31 Business Forum V1 + Ecosystem Registry (JSON, CSV, Excel .xlsx),
           GREENHOPE_MASTER canonical profile, and the First 10 Verified Investor Knowledge Packs
  Stage 1: Verify, hash, sign & encrypt all 66 COP31 entities into the AES-256-GCM Security Vault
  Stage 2: Create 66 isolated per-investor KAG/RAG/Hybrid artifacts + initialize Central GreenHope KAG+Scoped RAG
  Stage 3: Run multi-sector form filling + GreenHope Anti-Hallucination Application Agent demos
  Stage 4: Package the full downloadable ZIP archive (`greenhope_cop31_investor_ai_project.zip`)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_greenhope_knowledge_packs import (
    build_ten_investor_knowledge_packs,
    write_greenhope_master_profile,
)
from scripts.build_registry_and_excel import (
    export_formatted_excel,
    export_json_and_csv,
    get_verified_cop31_investors,
    write_sample_applicant_projects,
)
from scripts.package_project_zip import build_project_zip
from src.forms.form_filler import COP31FormFiller
from src.models.greenhope_kag_rag import GreenHopeCentralKAGRAG
from src.models.investor_model_factory import PerInvestorModelFactory
from src.models.schemas import ApplicantProject, SecurityRole
from src.security.vault import InvestorSecurityVault

DEMO_PASSPHRASE = os.getenv("COP31_VAULT_PASSPHRASE", "COP31-Antalya-2026-Secure-Vault-Demo!")


def main() -> None:
    data_dir = PROJECT_ROOT / "data"
    vault_dir = data_dir / "secured_vault"
    models_dir = PROJECT_ROOT / "investor_models"
    packs_dir = PROJECT_ROOT / "investors"
    filled_dir = PROJECT_ROOT / "outputs" / "filled_forms"
    report_path = PROJECT_ROOT / "outputs" / "COP31_KAG_RAG_System_Report.md"

    audit_file = vault_dir / "audit_log.jsonl"
    if audit_file.exists():
        audit_file.unlink()

    print("=== STAGE 0: Compiling 66-Entity COP31 Investor Universe + GREENHOPE_MASTER + 10 Knowledge Packs ===")
    investors = get_verified_cop31_investors()
    export_json_and_csv(investors, data_dir)
    export_formatted_excel(investors, data_dir / "COP31_Investors_Banks_Registry.xlsx")
    write_sample_applicant_projects(data_dir / "sample_applicant_projects.json")
    write_greenhope_master_profile(data_dir / "greenhope_master.json")
    packs = build_ten_investor_knowledge_packs(investors, packs_dir)
    print(f"Compiled {len(investors)} verified COP31 entities + GREENHOPE_MASTER + {len(packs)} P1 Investor Knowledge Packs.")

    print("\n=== STEP 1: Securing 66-Entity Registry (AES-256-GCM + Merkle Root + HMAC + RBAC + Audit Chain) ===")
    vault = InvestorSecurityVault(vault_dir)
    vault.seal_registry(
        investors=investors,
        passphrase=DEMO_PASSPHRASE,
        actor="cop31_security_admin",
        role=SecurityRole.ADMIN,
    )
    verify_res = vault.verify_integrity(
        passphrase=DEMO_PASSPHRASE,
        actor="cop31_security_officer",
        role=SecurityRole.SECURITY_OFFICER,
    )
    print(f"Vault sealed & verified! Backend={verify_res['crypto_backend']}, Records={verify_res['record_count']}, MerkleRoot={verify_res['merkle_root_sha256'][:20]}...")

    print("\n=== STEP 2: Building 66 Isolated Investor Artifacts + Central GreenHope KAG/RAG Scoped Engine ===")
    factory = PerInvestorModelFactory(vault=vault, models_root=models_dir)
    manifests = factory.build_all_models_from_secured_vault(
        passphrase=DEMO_PASSPHRASE,
        actor="cop31_model_engineer",
        role=SecurityRole.MODEL_ENGINEER,
    )
    kag_cnt = sum(1 for m in manifests if m.model_architecture.value == "KAG")
    rag_cnt = sum(1 for m in manifests if m.model_architecture.value == "RAG")
    hyb_cnt = sum(1 for m in manifests if m.model_architecture.value == "HYBRID_KAG_RAG")
    print(f"Built {len(manifests)} isolated per-investor artifacts -> KAG: {kag_cnt}, RAG: {rag_cnt}, HYBRID_KAG_RAG: {hyb_cnt}")

    central = GreenHopeCentralKAGRAG(
        investors=investors,
        greenhope_master_path=data_dir / "greenhope_master.json",
        knowledge_packs_dir=packs_dir,
    )
    cmp_bbva_ziraat = central.compare_investors("inv_bbva_group", "inv_ziraat_bankasi")
    print(
        f"Central KAG+RAG Loaded: {central.graph.number_of_nodes()} KG nodes, {central.graph.number_of_edges()} KG edges, "
        f"{len(central.rag_chunks)} scoped RAG chunks | BBVA vs Ziraat winner: {cmp_bbva_ziraat['recommended_name']}"
    )

    print("\n=== STEP 3: Auto-Filling Sample Forms (Multi-Sector + GreenHope Application Agent) ===")
    projects_raw = json.loads((data_dir / "sample_applicant_projects.json").read_text(encoding="utf-8"))
    projects = {p["project_id"]: ApplicantProject.model_validate(p) for p in projects_raw["projects"]}
    filler = COP31FormFiller(vault=vault, model_factory=factory)

    demo_pairs = [
        ("inv_ebrd", "proj_anatolia_green_steel_solar"),
        ("inv_ifc", "proj_anatolia_green_steel_solar"),
        ("inv_garanti_bbva", "proj_anatolia_green_steel_solar"),
        ("inv_bbva_group", "proj_anatolia_green_steel_solar"),
        ("inv_halkbank", "proj_antalya_agri_adaptation_sme"),
        ("inv_gcf", "proj_antalya_agri_adaptation_sme"),
        ("inv_bii_uk", "proj_em_grid_flex_storage"),
        ("inv_gfanz_ccr", "proj_em_grid_flex_storage"),
    ]
    demo_results = []
    for inv_id, proj_id in demo_pairs:
        packet = filler.fill_investor_form(
            investor_id=inv_id,
            project=projects[proj_id],
            passphrase=DEMO_PASSPHRASE,
            actor="cop31_form_operator",
            role=SecurityRole.FORM_OPERATOR,
        )
        json_p, md_p = filler.export_packet(packet, filled_dir)
        demo_results.append((packet, json_p, md_p))

    # Also export GreenHope Application Agent drafts for Top 3 Immediate Attack Targets (BBVA, AIIB, World Bank)
    for gh_inv in ["inv_bbva_group", "inv_aiib", "inv_world_bank_ibrd"]:
        draft = central.run_application_agent(gh_inv)
        (filled_dir / f"greenhope_draft__{gh_inv}.json").write_text(
            json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    chain_ok, audit_count = vault.verify_audit_chain(actor="cop31_auditor", role=SecurityRole.AUDITOR)
    print(f"Audit Chain Verified: {chain_ok} ({audit_count} hash-chained entries).")

    # Write concise executive report
    lines = [
        "# GreenHope × COP31 Antalya (Nov 2026) Investor Intelligence & KAG/RAG System Report",
        "",
        "## 1. Step 1 Security & Verification Summary",
        f"- **Verified COP31 Entities Secured:** `{verify_res['record_count']}` (distinguishing `Investor Confirmed`, `Finance Participant`, `COP31 Supporter`, and `Potential Strategic Partner`)",
        f"- **Encryption Standard:** `AES-256-GCM` (`{verify_res['crypto_backend']}`) + PBKDF2-HMAC-SHA256 (600,000 iterations) + Merkle Root + HMAC-SHA256 Manifest",
        f"- **Merkle Root:** `{verify_res['merkle_root_sha256']}`",
        f"- **Tamper-Evident Audit Log:** `{audit_count}` verified hash-chained entries",
        "- **IP Anti-Copying Protection:** 4-Tier Classification (`LEVEL_1_PUBLIC` -> `LEVEL_4_RESTRICTED`); `AUTO-FILL -> REVIEW -> APPROVE -> SUBMIT` human approval gate.",
        "",
        "## 2. Step 2 Central KAG + Scoped RAG & 10 Verified Investor Knowledge Packs",
        f"- **Central Knowledge Graph:** `{central.graph.number_of_nodes()}` nodes, `{central.graph.number_of_edges()}` typed edges linking `GreenHope` (7 domains) to all 66 COP31 entities.",
        f"- **Central Scoped RAG Index:** `{len(central.rag_chunks)}` verified chunks across all 66 entities + **10 P1 Knowledge Packs** (`investors/bbva/`, `garanti_bbva/`, `aiib/`, `world_bank/`, `qnb/`, `meridiam/`, `m_and_g/`, `hsbc/`, `akbank/`, `denizbank/`).",
        f"- **Isolated Per-Investor Artifacts:** `{len(manifests)}` directories (`KAG={kag_cnt}`, `RAG={rag_cnt}`, `HYBRID={hyb_cnt}`).",
        "",
        "## 3. Immediate COP31 Antalya Action Targets",
        "1. **BBVA / Garanti BBVA (P1, Tier A):** Climate Finance Hub pavilion (Green Zone); bridging innovation to investment for GreenHope city pilots.",
        "2. **AIIB (P1, Tier A — TOMORROW NOV 16 EVENT):** $1.6B Türkiye climate package + Nov 14 AIIB–GGGI project-preparation cooperation.",
        "3. **World Bank Group / IFC (P1, Tier A):** Target via urban resilience country programs, guarantees & IFC private-sector pathways.",
        "4. **COP31 Startup Zone / Investor Lounge (3,600 m², Green Zone):** One-to-one investor/startup meetings.",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n=== STAGE 4: Packaging Complete Downloadable Project ZIP ===")
    build_project_zip()


if __name__ == "__main__":
    main()
