"""CLI for the COP31 Secured Investor Registry & Per-Investor KAG/RAG Form-Filling System."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .forms.form_filler import COP31FormFiller
from .models.investor_model_factory import PerInvestorModelFactory
from .models.schemas import ApplicantProject, InvestorRecord, SecurityRole
from .security.vault import InvestorSecurityVault

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_JSON = PROJECT_ROOT / "data" / "cop31_investors_verified.json"
DEFAULT_VAULT_DIR = PROJECT_ROOT / "data" / "secured_vault"
DEFAULT_MODELS_DIR = PROJECT_ROOT / "investor_models"
DEFAULT_PROJECTS_JSON = PROJECT_ROOT / "data" / "sample_applicant_projects.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "filled_forms"


def _get_passphrase(args_passphrase: str | None) -> str:
    pw = args_passphrase or os.getenv("COP31_VAULT_PASSPHRASE")
    if not pw:
        print(
            "ERROR: Provide vault passphrase via --passphrase or environment variable COP31_VAULT_PASSPHRASE.",
            file=sys.stderr,
        )
        sys.exit(2)
    return pw


def main() -> None:
    parser = argparse.ArgumentParser(
        description="COP31 Antalya 2026 Secured Investor Registry & Per-Investor KAG/RAG Form-Filling CLI"
    )
    parser.add_argument("--passphrase", help="Vault passphrase (or set COP31_VAULT_PASSPHRASE env var)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("seal", help="Step 1: Verify & encrypt the COP31 investor list into the AES-256-GCM Security Vault")
    sub.add_parser("verify", help="Step 1: Verify vault ciphertext hash, HMAC signature, AES-GCM tag & Merkle root")
    sub.add_parser("audit", help="Step 1: Verify the SHA-256 hash-chained audit trail")
    sub.add_parser("build-models", help="Step 2: Build isolated KAG/RAG/Hybrid models for EVERY verified COP31 investor")

    match_p = sub.add_parser("match", help="Step 3: Rank top matching COP31 investors for an applicant project")
    match_p.add_argument("--project-id", required=True, help="Project ID from sample_applicant_projects.json or custom file")
    match_p.add_argument("--projects-file", default=str(DEFAULT_PROJECTS_JSON))
    match_p.add_argument("--top-n", type=int, default=8)

    fill_p = sub.add_parser("fill-form", help="Step 3: Auto-fill a specific investor's form using its isolated KAG/RAG model")
    fill_p.add_argument("--investor-id", required=True, help="Investor ID (e.g., inv_ebrd, inv_gcf, inv_garanti_bbva)")
    fill_p.add_argument("--project-id", required=True, help="Project ID to populate the form for")
    fill_p.add_argument("--projects-file", default=str(DEFAULT_PROJECTS_JSON))
    fill_p.add_argument("--out-dir", default=str(DEFAULT_OUTPUT_DIR))

    args = parser.parse_args()
    vault = InvestorSecurityVault(DEFAULT_VAULT_DIR)
    factory = PerInvestorModelFactory(vault=vault, models_root=DEFAULT_MODELS_DIR)

    if args.command == "audit":
        ok, count = vault.verify_audit_chain(actor="cli_auditor", role=SecurityRole.AUDITOR)
        print(json.dumps({"audit_chain_valid": ok, "entries_verified": count}, indent=2))
        return

    pw = _get_passphrase(args.passphrase)

    if args.command == "seal":
        raw = json.loads(DEFAULT_REGISTRY_JSON.read_text(encoding="utf-8"))
        investors = [InvestorRecord.model_validate(item) for item in raw["investors"]]
        manifest = vault.seal_registry(investors=investors, passphrase=pw, actor="cli_admin", role=SecurityRole.ADMIN)
        print(json.dumps({k: v for k, v in manifest.items() if k != "record_hashes"}, indent=2))
    elif args.command == "verify":
        res = vault.verify_integrity(passphrase=pw, actor="cli_security_officer", role=SecurityRole.SECURITY_OFFICER)
        print(json.dumps(res, indent=2))
    elif args.command == "build-models":
        manifests = factory.build_all_models_from_secured_vault(
            passphrase=pw,
            actor="cli_model_engineer",
            role=SecurityRole.MODEL_ENGINEER,
        )
        print(f"Successfully built {len(manifests)} isolated per-investor KAG/RAG models in {DEFAULT_MODELS_DIR}")
    elif args.command in {"match", "fill-form"}:
        projects_raw = json.loads(Path(args.projects_file).read_text(encoding="utf-8"))
        proj_map = {p["project_id"]: ApplicantProject.model_validate(p) for p in projects_raw["projects"]}
        if args.project_id not in proj_map:
            print(f"Unknown project_id '{args.project_id}'. Available: {list(proj_map.keys())}", file=sys.stderr)
            sys.exit(2)
        project = proj_map[args.project_id]
        filler = COP31FormFiller(vault=vault, model_factory=factory)

        if args.command == "match":
            ranked = filler.rank_matching_investors(project=project, passphrase=pw, top_n=args.top_n)
            for idx, (inv, ev) in enumerate(ranked, start=1):
                print(
                    f"{idx:2d}. {inv.name} ({inv.investor_id}) | Model={inv.recommended_ai_model_type.value:14s} "
                    f"| Eligible={str(ev.eligible):5s} | Fit={ev.fit_score:5.1f} | Instrument={ev.recommended_instrument}"
                )
        else:
            packet = filler.fill_investor_form(investor_id=args.investor_id, project=project, passphrase=pw)
            json_path, md_path = filler.export_packet(packet, Path(args.out_dir))
            print(
                json.dumps(
                    {
                        "submission_id": packet.submission_id,
                        "investor_id": packet.investor_id,
                        "model_architecture": packet.model_architecture.value,
                        "eligible": packet.eligibility.eligible,
                        "fit_score": packet.eligibility.fit_score,
                        "completion_rate_percent": packet.completion_rate_percent,
                        "average_confidence": packet.average_confidence,
                        "json_export": str(json_path),
                        "markdown_export": str(md_path),
                    },
                    indent=2,
                )
            )


if __name__ == "__main__":
    main()
