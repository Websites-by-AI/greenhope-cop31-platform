"""Comprehensive pytest suite for Step 1 Security Vault, Step 2 Per-Investor KAG/RAG Models, and Step 3 Automated Form Filling."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_registry_and_excel import get_verified_cop31_investors
from src.forms.form_filler import COP31FormFiller
from src.models.investor_model_factory import PerInvestorModelFactory
from src.models.schemas import (
    AIModelArchitecture,
    ApplicantProject,
    FieldFillStatus,
    FormTemplateType,
    SecurityRole,
)
from src.security.crypto_engine import (
    CryptoEngineError,
    decrypt_aes256_gcm,
    derive_master_key,
    encrypt_aes256_gcm,
    generate_salt,
)
from src.security.tenant_guard import PIIRedactor, TenantIsolationError, TenantIsolationGuard
from src.security.vault import AccessDeniedError, InvestorSecurityVault, VaultIntegrityError

TEST_PASSPHRASE = "Test-COP31-Antalya-Strong-Passphrase-2026!"


def _make_sample_project(**overrides) -> ApplicantProject:
    base = {
        "project_id": "proj_test_01",
        "project_title": "Antalya Solar & Green Steel Plant",
        "organization_name": "Test Clean Industry A.S.",
        "applicant_type": "Large Corporate",
        "country": "Türkiye",
        "region": "EMEA",
        "tax_or_registration_id": "VKN-1234567890",
        "contact_email": "cfo@testclean.example.tr",
        "contact_phone": "+90 242 555 1234",
        "iban_or_account": "TR330006100519786457841326",
        "primary_sector": "Industrial Decarbonization",
        "secondary_sectors": ["Renewable Energy", "Energy Storage"],
        "requested_amount_usd": 35_000_000,
        "total_project_cost_usd": 75_000_000,
        "co_financing_committed_usd": 20_000_000,
        "preferred_instruments": ["Senior Debt", "Green Investment Loan"],
        "project_stage": "Ready-to-Build",
        "implementation_years": 4,
        "estimated_ghg_reduction_tco2e_per_year": 120_000.0,
        "adaptation_beneficiaries": 500,
        "annual_revenue_usd": 180_000_000.0,
        "ebitda_usd": 31_000_000.0,
        "expected_irr_percent": 15.2,
        "has_eia_and_permits": True,
        "has_paris_alignment_assessment": True,
        "has_nda_no_objection_letter": False,
        "has_second_party_opinion": True,
        "has_kgf_or_collateral": True,
        "shariah_compliant_structure": False,
        "women_or_youth_led": False,
        "eu_cbam_exporter": True,
        "fossil_fuel_involvement": False,
        "project_summary": "Green steel retrofit with contact cfo@testclean.example.tr and IBAN TR330006100519786457841326.",
        "climate_rationale": "Cuts industrial CO2 by 120,000 tCO2e/year aligned with Türkiye NDC.",
        "technology_and_innovation": "Electric arc furnace powered by 80 MW solar PV and BESS.",
        "esg_and_social_impact": "Creates 250 local engineering jobs with zero coal usage.",
        "key_risks_and_mitigants": "Mitigated via EUR export offtake contracts and fixed-price EPC.",
    }
    base.update(overrides)
    return ApplicantProject.model_validate(base)


def test_aes256_gcm_encrypt_decrypt_and_tamper_detection():
    salt = generate_salt(16)
    key = derive_master_key(TEST_PASSPHRASE, salt, iterations=10_000)
    plaintext = b"Verified COP31 Investor Secret Payload"
    aad = b"cop31-test-aad"

    env = encrypt_aes256_gcm(key, plaintext, aad=aad)
    assert decrypt_aes256_gcm(key, env, expected_aad=aad) == plaintext

    # Tamper AAD -> must raise
    with pytest.raises(CryptoEngineError):
        decrypt_aes256_gcm(key, env, expected_aad=b"wrong-aad")

    # Tamper ciphertext -> GCM auth tag MUST fail
    bad_env = dict(env)
    bad_env["ciphertext_b64"] = "A" + env["ciphertext_b64"][1:] if env["ciphertext_b64"][0] != "A" else "B" + env["ciphertext_b64"][1:]
    with pytest.raises(CryptoEngineError):
        decrypt_aes256_gcm(key, bad_env, expected_aad=aad)


def test_step1_vault_seal_verify_rbac_and_tamper_detection(tmp_path: Path):
    investors = get_verified_cop31_investors()
    assert len(investors) == 66

    vault = InvestorSecurityVault(tmp_path / "vault")

    # RBAC: FORM_OPERATOR must NOT be allowed to seal the vault
    with pytest.raises(AccessDeniedError):
        vault.seal_registry(investors, TEST_PASSPHRASE, actor="unauthorized_op", role=SecurityRole.FORM_OPERATOR)

    # Admin seals successfully
    manifest = vault.seal_registry(investors, TEST_PASSPHRASE, actor="admin", role=SecurityRole.ADMIN)
    assert manifest["record_count"] == 66

    # Security officer verifies successfully
    res = vault.verify_integrity(TEST_PASSPHRASE, actor="sec_officer", role=SecurityRole.SECURITY_OFFICER)
    assert res["verified"] is True
    assert res["record_count"] == 66

    # Wrong passphrase fails HMAC / GCM verification
    with pytest.raises(VaultIntegrityError):
        vault.verify_integrity("Wrong-Passphrase-999999!", actor="sec_officer", role=SecurityRole.SECURITY_OFFICER)

    # Audit chain integrity must pass and include the denied attempt
    ok, count = vault.verify_audit_chain(actor="auditor", role=SecurityRole.AUDITOR)
    assert ok is True
    assert count >= 4

    # Tampering the encrypted vault file must be detected immediately
    enc_text = vault.encrypted_file.read_text(encoding="utf-8")
    vault.encrypted_file.write_text(enc_text + " ", encoding="utf-8")
    with pytest.raises(VaultIntegrityError):
        vault.verify_integrity(TEST_PASSPHRASE, actor="sec_officer", role=SecurityRole.SECURITY_OFFICER)


def test_pii_redaction_and_tenant_isolation(tmp_path: Path):
    raw = "Send docs to cfo@example.com, IBAN TR330006100519786457841326, VKN: 4829103847, phone +90 242 555 0194."
    sanitized, token_map = PIIRedactor.redact_text(raw)
    assert "cfo@example.com" not in sanitized
    assert "TR330006100519786457841326" not in sanitized
    assert "4829103847" not in sanitized
    assert len(token_map) >= 3

    master_key = derive_master_key(TEST_PASSPHRASE, b"0123456789abcdef", iterations=10_000)
    tenant_salt = b"fedcba9876543210"
    guard_a = TenantIsolationGuard(tmp_path / "models", "inv_ebrd", master_key, tenant_salt)
    guard_b = TenantIsolationGuard(tmp_path / "models", "inv_garanti_bbva", master_key, tenant_salt)

    # Unique HKDF subkeys per investor
    assert guard_a.subkey_fingerprint != guard_b.subkey_fingerprint

    # Cross-tenant directory access MUST be blocked
    with pytest.raises(TenantIsolationError):
        guard_a.assert_path_within_tenant(guard_b.tenant_dir / "rag_corpus.json")

    # Cross-tenant investor_id payload MUST be blocked
    with pytest.raises(TenantIsolationError):
        guard_a.assert_investor_match("inv_garanti_bbva")


def test_step2_build_all_66_models_and_step3_form_filling(tmp_path: Path):
    investors = get_verified_cop31_investors()
    vault = InvestorSecurityVault(tmp_path / "vault")
    vault.seal_registry(investors, TEST_PASSPHRASE, actor="admin", role=SecurityRole.ADMIN)

    models_dir = tmp_path / "models"
    factory = PerInvestorModelFactory(vault=vault, models_root=models_dir)
    manifests = factory.build_all_models_from_secured_vault(
        passphrase=TEST_PASSPHRASE,
        actor="ml_engineer",
        role=SecurityRole.MODEL_ENGINEER,
    )
    assert len(manifests) == 66

    # Verify every investor got a unique tenant subkey fingerprint and proper KAG/RAG artifacts
    fingerprints = {m.tenant_key_fingerprint for m in manifests}
    assert len(fingerprints) == 66
    for m in manifests:
        tdir = models_dir / m.investor_id
        assert (tdir / "model_manifest.json").exists()
        assert (tdir / "form_schema.json").exists()
        if m.model_architecture in (AIModelArchitecture.KAG, AIModelArchitecture.HYBRID_KAG_RAG):
            assert (tdir / "knowledge_graph.json").exists()
            assert m.kag_nodes_count > 10
        if m.model_architecture in (AIModelArchitecture.RAG, AIModelArchitecture.HYBRID_KAG_RAG):
            assert (tdir / "rag_corpus.json").exists()
            assert m.rag_chunks_count >= 10

    # Test Step 3 Form Filling across KAG, RAG, and HYBRID models
    filler = COP31FormFiller(vault=vault, model_factory=factory)
    project = _make_sample_project()

    # 1. KAG model (EBRD)
    pkt_kag = filler.fill_investor_form("inv_ebrd", project, TEST_PASSPHRASE)
    assert pkt_kag.model_architecture == AIModelArchitecture.KAG
    assert pkt_kag.eligibility.eligible is True
    assert pkt_kag.eligibility.kag_hops_executed == 6
    assert any(f.kag_reasoning_path for f in pkt_kag.fields)
    # Ensure PII was redacted from summary
    summary_blob = " ".join(str(f.value) for f in pkt_kag.fields)
    assert "cfo@testclean.example.tr" not in summary_blob
    assert "TR330006100519786457841326" not in summary_blob

    # 2. KAG strict compliance check on GCF (missing NDA letter -> MISSING_REQUIRED_DATA)
    pkt_gcf = filler.fill_investor_form("inv_gcf", project, TEST_PASSPHRASE)
    nda_field = next(f for f in pkt_gcf.fields if f.field_id == "nda_no_objection_status")
    assert nda_field.status == FieldFillStatus.MISSING_REQUIRED_DATA

    # 3. KAG strict exclusion check: fossil fuel project must fail eligibility
    fossil_proj = _make_sample_project(fossil_fuel_involvement=True)
    pkt_fossil = filler.fill_investor_form("inv_ebrd", fossil_proj, TEST_PASSPHRASE)
    assert pkt_fossil.eligibility.eligible is False
    assert any("EXCLUSION" in c.upper() for c in pkt_fossil.eligibility.failed_checks)

    # 4. RAG model (Garanti BBVA) -> must contain RAG citations
    pkt_rag = filler.fill_investor_form("inv_garanti_bbva", project, TEST_PASSPHRASE)
    assert pkt_rag.model_architecture == AIModelArchitecture.RAG
    assert any(len(f.rag_citations) > 0 for f in pkt_rag.fields)

    # 5. HYBRID KAG+RAG model (IFC) -> must contain BOTH KAG reasoning path AND RAG citations
    pkt_hyb = filler.fill_investor_form("inv_ifc", project, TEST_PASSPHRASE)
    assert pkt_hyb.model_architecture == AIModelArchitecture.HYBRID_KAG_RAG
    assert any(f.kag_reasoning_path for f in pkt_hyb.fields)
    assert any(len(f.rag_citations) > 0 for f in pkt_hyb.fields)

    # 6. Regional mandate precision: IDB (Latin America) & AfDB (Africa) must NOT falsely match a Türkiye project
    pkt_idb = filler.fill_investor_form("inv_idb", project, TEST_PASSPHRASE)
    assert pkt_idb.eligibility.eligible is False
    pkt_afdb = filler.fill_investor_form("inv_afdb", project, TEST_PASSPHRASE)
    assert pkt_afdb.eligibility.eligible is False

    # 7. Model artifact tamper detection: alter EBRD KG -> loading MUST raise VaultIntegrityError
    kg_file = models_dir / "inv_ebrd" / "knowledge_graph.json"
    kg_file.write_text(kg_file.read_text(encoding="utf-8") + "\n ", encoding="utf-8")
    with pytest.raises(VaultIntegrityError):
        filler.fill_investor_form("inv_ebrd", project, TEST_PASSPHRASE)


def test_greenhope_knowledge_packs_central_kag_rag_ip_guard_and_zero_hallucination(tmp_path: Path):
    import zipfile
    from scripts.build_greenhope_knowledge_packs import (
        build_ten_investor_knowledge_packs,
        write_greenhope_master_profile,
    )
    from src.models.greenhope_kag_rag import GreenHopeCentralKAGRAG
    from src.models.schemas import RelationshipStatus

    investors = get_verified_cop31_investors()
    by_id = {i.investor_id: i for i in investors}

    # Governance Rule: Supporters like Siemens MUST NOT be labeled Investor Confirmed
    assert by_id["inv_siemens"].relationship_status == RelationshipStatus.COP31_SUPPORTER
    assert by_id["inv_bbva_group"].relationship_status == RelationshipStatus.INVESTOR_CONFIRMED
    assert by_id["inv_aiib"].relationship_status == RelationshipStatus.INVESTOR_CONFIRMED

    master_path = tmp_path / "greenhope_master.json"
    write_greenhope_master_profile(master_path)
    packs_dir = tmp_path / "investors"
    packs = build_ten_investor_knowledge_packs(investors, packs_dir)
    assert len(packs) == 10
    for p in packs:
        pdir = packs_dir / p["slug"]
        assert (pdir / "identity.md").exists()
        assert (pdir / "climate_strategy.md").exists()
        assert (pdir / "investment_policy.md").exists()
        assert (pdir / "cop31_events.md").exists()
        assert (pdir / "contacts.md").exists()
        assert (pdir / "application_questions.json").exists()
        assert (pdir / "evidence" / "verified_claims.json").exists()

    central = GreenHopeCentralKAGRAG(investors, master_path, packs_dir)

    # Evidence-based comparator: BBVA beats Ziraat Bankası for GreenHope
    cmp_res = central.compare_investors("inv_bbva_group", "inv_ziraat_bankasi")
    assert cmp_res["recommended_target"] == "inv_bbva_group"

    # Scoped RAG returns only BBVA chunks when scoped to inv_bbva_group
    rag_res = central.query_scoped_rag("Climate Finance Hub cleantech", investor_id="inv_bbva_group", top_k=4)
    assert len(rag_res["results"]) >= 2
    assert all(r["investor_id"] == "inv_bbva_group" for r in rag_res["results"])

    # Application Agent: Zero Hallucination + 4-Tier IP Security
    draft = central.run_application_agent("inv_bbva_group")
    rev = next(f for f in draft["fields"] if f["field_id"] == "annual_revenue")
    assert rev["answer"] is None
    assert rev["status"] == "MISSING_INFORMATION"
    assert rev["action"] == "ASK_USER"

    ip_field = next(f for f in draft["fields"] if f["field_id"] == "ip_and_proprietary_algorithms")
    assert ip_field["answer"] is None
    assert ip_field["status"] == "BLOCKED_BY_IP_SECURITY"

    # Supporter Warning Guard fires on Siemens
    sup_draft = central.run_application_agent("inv_siemens")
    assert sup_draft["supporter_warning"] is not None
    assert "COP31 Supporter" in sup_draft["supporter_warning"]

    # Level 4 Restricted secret cannot be edited via master API
    with pytest.raises(PermissionError):
        central.update_master_field("restricted_secrets", "leaked-key")


def test_investor_crm_pipeline_persistence_stage_advance_and_csv_export(tmp_path: Path):
    from src.crm.pipeline_store import InvestorCRMPipeline

    investors = get_verified_cop31_investors()
    crm_file = tmp_path / "crm.json"
    crm = InvestorCRMPipeline(crm_file, investors)

    data = crm.list_pipeline()
    assert data["total"] == 66
    assert crm.records["inv_bbva_group"]["stage"] == "Meeting Booked"
    assert crm.records["inv_aiib"]["stage"] == "Meeting Booked"

    # Update a record & verify persistence across reload
    crm.update_record(
        "inv_meridiam",
        stage="Submitted",
        owner="GreenHope Infra Lead",
        next_action="Follow up at COP31 Infrastructure Track",
    )
    crm_reloaded = InvestorCRMPipeline(crm_file, investors)
    assert crm_reloaded.records["inv_meridiam"]["stage"] == "Submitted"
    assert crm_reloaded.records["inv_meridiam"]["owner"] == "GreenHope Infra Lead"

    # Auto-advancing stage never downgrades a further stage (Submitted stays Submitted)
    crm_reloaded.advance_stage_if_earlier("inv_meridiam", "Draft Auto-Filled")
    assert crm_reloaded.records["inv_meridiam"]["stage"] == "Submitted"

    # Auto-advancing earlier stage promotes cleanly & increments submitted_docs_count
    crm_reloaded.advance_stage_if_earlier("inv_qnb_turkiye", "Human Approved", increment_docs=True)
    assert crm_reloaded.records["inv_qnb_turkiye"]["stage"] == "Human Approved"
    assert crm_reloaded.records["inv_qnb_turkiye"]["submitted_docs_count"] == 1

    csv_out = crm_reloaded.export_csv_text()
    assert "inv_bbva_group" in csv_out and "Meeting Booked" in csv_out


