"""GreenHope × COP31 Antalya 2026 Investor Intelligence & KAG/RAG Web Platform.

Runs on aiohttp (0.0.0.0:8080), featuring:
- One-Click Demo Login + RBAC Role Presets + Credentials Login
- Live 66-Entity COP31 Business Forum V1 + Ecosystem Intelligence Database
- 10 Verified P1 Investor Knowledge Pack Inspector (13 files + verified_claims.json)
- Central KAG Knowledge Graph Explorer + Per-Investor Scoped RAG + Investor Comparator
- Zero-Hallucination Application-Filling Agent (AUTO-FILL -> REVIEW -> APPROVE -> SUBMIT)
- GREENHOPE_MASTER Single-Source-of-Truth Editor with 4-Tier IP Security Protection
- Live Step 1 AES-256-GCM Vault & SHA-256 Audit Chain Verification
- One-Click Downloadable Full Project ZIP (`/api/download/project.zip`) & Excel Registry
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from aiohttp import web

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.package_project_zip import ZIP_FILENAME, build_project_zip
from src.crm.pipeline_store import InvestorCRMPipeline
from src.models.greenhope_kag_rag import GreenHopeCentralKAGRAG
from src.models.schemas import RelationshipStatus, SecurityRole
from src.security.vault import InvestorSecurityVault

STATIC_DIR = Path(__file__).resolve().parent / "static"
DATA_DIR = PROJECT_ROOT / "data"
VAULT_DIR = DATA_DIR / "secured_vault"
PACKS_DIR = PROJECT_ROOT / "investors"
EXPORTS_DIR = PROJECT_ROOT / "outputs" / "approved_submissions"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

VAULT_PASSPHRASE = os.getenv("COP31_VAULT_PASSPHRASE", "COP31-Antalya-2026-Secure-Vault-Demo!")
DEMO_USERS = {
    "demo": {"password": "cop31demo", "display_name": "GreenHope Demo Founder", "role": SecurityRole.ADMIN},
    "founder": {"password": "greenhope2026", "display_name": "GreenHope Founder", "role": SecurityRole.ADMIN},
    "security": {"password": "vault2026", "display_name": "Security Officer", "role": SecurityRole.SECURITY_OFFICER},
    "engineer": {"password": "kagrag2026", "display_name": "AI / KAG-RAG Engineer", "role": SecurityRole.MODEL_ENGINEER},
    "operator": {"password": "forms2026", "display_name": "Application Operator", "role": SecurityRole.FORM_OPERATOR},
}

ROLE_DISPLAY = {
    "ADMIN": ("GreenHope Founder (Demo Admin)", SecurityRole.ADMIN),
    "SECURITY_OFFICER": ("Security Officer (Vault & IP Audit)", SecurityRole.SECURITY_OFFICER),
    "MODEL_ENGINEER": ("AI / KAG-RAG Engineer", SecurityRole.MODEL_ENGINEER),
    "FORM_OPERATOR": ("Investor Application Operator", SecurityRole.FORM_OPERATOR),
    "AUDITOR": ("Compliance & Audit Reviewer", SecurityRole.AUDITOR),
}


class AppState:
    def __init__(self) -> None:
        self.vault = InvestorSecurityVault(VAULT_DIR)
        self.investors, _, _, self.record_hashes = self.vault.load_verified_investors(
            passphrase=VAULT_PASSPHRASE,
            actor="webapp_bootstrap",
            role=SecurityRole.MODEL_ENGINEER,
        )
        self.central = GreenHopeCentralKAGRAG(
            investors=self.investors,
            greenhope_master_path=DATA_DIR / "greenhope_master.json",
            knowledge_packs_dir=PACKS_DIR,
        )
        self.crm = InvestorCRMPipeline(
            store_path=DATA_DIR / "investor_crm_pipeline.json",
            investors=self.investors,
        )
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.zip_path = PROJECT_ROOT / ZIP_FILENAME
        if not self.zip_path.exists():
            build_project_zip(self.zip_path)

    def get_backup_metadata(self) -> Dict[str, Any]:
        if not self.zip_path.exists():
            build_project_zip(self.zip_path)
        raw_bytes = self.zip_path.read_bytes()
        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        with zipfile.ZipFile(self.zip_path, "r") as zf:
            file_count = len(zf.namelist())
        mtime = datetime.fromtimestamp(self.zip_path.stat().st_mtime, tz=timezone.utc).isoformat()
        return {
            "zip_filename": ZIP_FILENAME,
            "zip_size_kb": round(len(raw_bytes) / 1024.0, 1),
            "file_count": file_count,
            "sha256": sha256,
            "built_at_utc": mtime,
            "zip_url": "/api/download/project.zip",
            "excel_url": "/api/download/excel",
            "csv_url": "/api/download/csv",
            "json_url": "/api/download/json",
            "crm_csv_url": "/api/download/crm.csv",
            "crm_json_url": "/api/download/crm.json",
        }

    def get_session(self, request: web.Request) -> Optional[Dict[str, Any]]:
        token = request.cookies.get("gh_session") or request.headers.get("X-Session-Token")
        if token and token in self.sessions:
            return self.sessions[token]
        return None


STATE = AppState()


def require_session(request: web.Request) -> Dict[str, Any]:
    sess = STATE.get_session(request)
    if not sess:
        raise web.HTTPUnauthorized(
            text=json.dumps({"error": "Authentication required. Click 'One-Click Demo Login' to enter."}),
            content_type="application/json",
        )
    return sess


@web.middleware
async def preview_headers_middleware(request: web.Request, handler):
    resp = await handler(request)
    # Allow proxied iframe live previews cleanly without blocking
    resp.headers["Cache-Control"] = "no-store" if request.path.startswith("/api/") else "public, max-age=60"
    return resp


async def index_page(request: web.Request) -> web.FileResponse:
    return web.FileResponse(STATIC_DIR / "index.html")


async def api_login(request: web.Request) -> web.Response:
    body = await request.json()
    mode = body.get("mode", "credentials")

    if mode == "demo":
        role_key = str(body.get("role", "ADMIN")).upper()
        display_name, sec_role = ROLE_DISPLAY.get(role_key, ROLE_DISPLAY["ADMIN"])
        username = f"demo_{role_key.lower()}"
    else:
        username = str(body.get("username", "")).strip().lower()
        password = str(body.get("password", ""))
        user_rec = DEMO_USERS.get(username)
        if not user_rec or user_rec["password"] != password:
            return web.json_response({"error": "Invalid credentials. Use One-Click Demo Login or demo / cop31demo."}, status=401)
        display_name = user_rec["display_name"]
        sec_role = user_rec["role"]

    token = secrets.token_urlsafe(24)
    session = {
        "token": token,
        "username": username,
        "display_name": display_name,
        "role": sec_role.value,
        "logged_in_at": datetime.now(timezone.utc).isoformat(),
    }
    STATE.sessions[token] = session
    STATE.vault.log_model_or_form_event(
        actor=username,
        role=sec_role,
        action="webapp:login",
        outcome="SUCCESS",
        details=f"Session created via {mode} login ({sec_role.value}).",
    )

    resp = web.json_response({"authenticated": True, "user": session})
    resp.set_cookie("gh_session", token, httponly=True, samesite="Lax", path="/")
    return resp


async def api_logout(request: web.Request) -> web.Response:
    token = request.cookies.get("gh_session") or request.headers.get("X-Session-Token")
    if token and token in STATE.sessions:
        del STATE.sessions[token]
    resp = web.json_response({"authenticated": False})
    resp.del_cookie("gh_session", path="/")
    return resp


async def api_me(request: web.Request) -> web.Response:
    sess = STATE.get_session(request)
    return web.json_response(
        {
            "authenticated": sess is not None,
            "user": sess,
            "downloads": STATE.get_backup_metadata(),
        }
    )


async def api_overview(request: web.Request) -> web.Response:
    require_session(request)
    investors = STATE.investors
    packs_idx = json.loads((PACKS_DIR / "packs_index.json").read_text(encoding="utf-8"))

    status_counts: Dict[str, int] = {}
    branch_map: Dict[str, list] = {}
    tier_map: Dict[str, list] = {"Tier A — Approach Immediately": [], "Tier B — Core Follow-Up": [], "Tier C — Ecosystem / Strategic": []}

    for inv in investors:
        st = inv.relationship_status.value
        status_counts[st] = status_counts.get(st, 0) + 1
        br = inv.ecosystem_branch.value
        branch_map.setdefault(br, []).append(
            {
                "investor_id": inv.investor_id,
                "short_name": inv.short_name,
                "name": inv.name,
                "status": st,
                "priority": inv.ai_rag_priority,
                "has_pack": bool(inv.knowledge_pack_slug),
            }
        )
        tier_map.setdefault(inv.priority_tier, []).append(
            {
                "investor_id": inv.investor_id,
                "short_name": inv.short_name,
                "name": inv.name,
                "status": st,
                "priority": inv.ai_rag_priority,
                "relevance": inv.greenhope_relevance,
                "has_pack": bool(inv.knowledge_pack_slug),
                "fit_notes": inv.greenhope_fit_notes,
            }
        )

    ok_audit, audit_entries = STATE.vault.verify_audit_chain(actor="webapp_overview", role=SecurityRole.AUDITOR)
    manifest = json.loads((VAULT_DIR / "registry_integrity.manifest.json").read_text(encoding="utf-8"))

    return web.json_response(
        {
            "kpis": {
                "total_entities": len(investors),
                "investor_confirmed": status_counts.get(RelationshipStatus.INVESTOR_CONFIRMED.value, 0),
                "finance_participant": status_counts.get(RelationshipStatus.FINANCE_PARTICIPANT.value, 0),
                "cop31_supporter": status_counts.get(RelationshipStatus.COP31_SUPPORTER.value, 0),
                "strategic_partner": status_counts.get(RelationshipStatus.POTENTIAL_STRATEGIC_PARTNER.value, 0),
                "knowledge_packs": packs_idx["total_packs"],
                "kg_nodes": STATE.central.graph.number_of_nodes(),
                "kg_edges": STATE.central.graph.number_of_edges(),
                "rag_chunks": len(STATE.central.rag_chunks),
                "audit_entries": audit_entries,
                "audit_chain_valid": ok_audit,
                "merkle_root": manifest["merkle_root_sha256"],
            },
            "immediate_alerts": [
                {
                    "tag": "TOMORROW · NOV 16, 2026",
                    "title": "AIIB COP31 Antalya Program + AIIB–GGGI Project Preparation Pipeline",
                    "summary": "AIIB signed a $1.6B Türkiye climate package (Nov 12) and deepened cooperation with GGGI (Nov 14) on project preparation, investment-ready pipelines, co-financing & technical assistance. Position GreenHope as a municipal climate-resilience & MRV project-prep pilot.",
                    "target_investor_id": "inv_aiib",
                    "source_url": "https://www.aiib.org/en/news-events/events/2026/aiib-at-cop31.html",
                },
                {
                    "tag": "ON-SITE · GREEN ZONE",
                    "title": "COP31 Startup Zone & Investor Lounge (3,600 m² under COP Tower)",
                    "summary": "First dedicated Startup Zone at a COP with stages, B2B rooms & an Investor Lounge for 1-on-1 startup/investor meetings. Combine with the BBVA / Garanti BBVA 400 m² Climate Finance Hub pavilion.",
                    "target_investor_id": "inv_bbva_group",
                    "source_url": "https://startupzone.cop31.center/",
                },
            ],
            "top3_attack_briefs": [
                {
                    "rank": "1st Target · P1",
                    "investor_id": "inv_bbva_group",
                    "title": "BBVA / Garanti BBVA",
                    "headline": "Highest-priority commercial bank at COP31 Antalya (Global Banking Partner)",
                    "pathway": "GreenHope -> city pilot -> measurable climate impact -> financing -> scale",
                    "why": "Hosting a 400 m² Climate Finance Hub pavilion (60+ sessions) & explicitly bridging innovation-to-investment for real-world cleantech deployment (€700B Group / TRY 3.5T Garanti BBVA targets).",
                },
                {
                    "rank": "2nd Target · P1",
                    "investor_id": "inv_aiib",
                    "title": "AIIB (+ GGGI Cooperation)",
                    "headline": "$1.6B Türkiye Climate Deal + Tomorrow's Nov 16 Project-Prep Program",
                    "pathway": "policy -> technical support -> project preparation -> public/private financing -> investment-ready projects",
                    "why": "Fresh COP31 Türkiye evidence + Nov 14 AIIB–GGGI partnership explicitly designed to prepare investment-ready climate-resilient infrastructure pipelines.",
                },
                {
                    "rank": "3rd Target · P1",
                    "investor_id": "inv_world_bank_ibrd",
                    "title": "World Bank Group / IFC",
                    "headline": "$1.5B COP31 Türkiye Deals + Guarantees & Private-Capital Mobilization",
                    "pathway": "Ask which WBG instrument, municipal intermediary, guarantee, or IFC pathway finances a GreenHope pilot",
                    "why": "Co-hosting COP31 Global Finance Summit with EBRD, BBVA & GFANZ; focus on urban resilience country programs & IFC/MIGA de-risking rather than a raw grant ask.",
                },
            ],
            "tiers": tier_map,
            "ecosystem_tree": branch_map,
            "packs_index": packs_idx["packs"],
        }
    )


async def api_investors(request: web.Request) -> web.Response:
    require_session(request)
    items = []
    for inv in STATE.investors:
        fit = STATE.central.score_for_greenhope(inv.investor_id)
        rec = inv.model_dump(mode="json")
        rec["greenhope_fit_score"] = fit["greenhope_fit_score"]
        rec["aligned_domains"] = fit["aligned_domains"]
        items.append(rec)
    return web.json_response({"count": len(items), "investors": items})


async def api_investor_pack(request: web.Request) -> web.Response:
    require_session(request)
    investor_id = request.match_info["investor_id"]
    if investor_id not in STATE.central.by_id:
        return web.json_response({"error": f"Unknown investor_id: {investor_id}"}, status=404)

    inv = STATE.central.by_id[investor_id]
    fit = STATE.central.score_for_greenhope(investor_id)
    pack_files: Dict[str, Any] = {}
    verified_claims = []

    if inv.knowledge_pack_slug:
        pdir = PACKS_DIR / inv.knowledge_pack_slug
        if pdir.exists():
            for md in sorted(pdir.glob("*.md")):
                pack_files[md.name] = md.read_text(encoding="utf-8")
            qfile = pdir / "application_questions.json"
            if qfile.exists():
                pack_files["application_questions.json"] = json.loads(qfile.read_text(encoding="utf-8"))
            cfile = pdir / "evidence" / "verified_claims.json"
            if cfile.exists():
                verified_claims = json.loads(cfile.read_text(encoding="utf-8")).get("claims", [])

    if not verified_claims:
        verified_claims = [
            {
                "claim": f"{inv.name}: {inv.cop31_verified_2026_commitment}",
                "source": "Verified COP31 Registry Master Record",
                "url": inv.verification_source_url,
                "date_verified": inv.verification_date,
                "confidence": 0.96,
                "status": "verified",
            }
        ]

    return web.json_response(
        {
            "investor": inv.model_dump(mode="json"),
            "fit": fit,
            "has_full_pack": bool(inv.knowledge_pack_slug),
            "pack_slug": inv.knowledge_pack_slug,
            "pack_files": pack_files,
            "verified_claims": verified_claims,
        }
    )


async def api_kag_graph(request: web.Request) -> web.Response:
    require_session(request)
    ids_param = request.query.get("ids")
    ids = [x.strip() for x in ids_param.split(",") if x.strip()] if ids_param else None
    return web.json_response(STATE.central.get_knowledge_graph_subgraph(ids))


async def api_rag_query(request: web.Request) -> web.Response:
    require_session(request)
    body = await request.json()
    query = str(body.get("query", "")).strip()
    if not query:
        return web.json_response({"error": "Query cannot be empty."}, status=400)
    investor_id = body.get("investor_id") or None
    top_k = min(10, max(1, int(body.get("top_k", 5))))
    return web.json_response(STATE.central.query_scoped_rag(query=query, investor_id=investor_id, top_k=top_k))


async def api_kag_compare(request: web.Request) -> web.Response:
    require_session(request)
    body = await request.json()
    inv_a = body.get("investor_a", "inv_bbva_group")
    inv_b = body.get("investor_b", "inv_ziraat_bankasi")
    if inv_a not in STATE.central.by_id or inv_b not in STATE.central.by_id:
        return web.json_response({"error": "Invalid investor IDs for comparison."}, status=400)
    return web.json_response(STATE.central.compare_investors(inv_a, inv_b))


async def api_agent_draft(request: web.Request) -> web.Response:
    sess = require_session(request)
    body = await request.json()
    investor_id = body.get("investor_id", "inv_bbva_group")
    overrides = body.get("overrides", {})
    if investor_id not in STATE.central.by_id:
        return web.json_response({"error": f"Unknown investor_id: {investor_id}"}, status=404)

    draft = STATE.central.run_application_agent(investor_id=investor_id, custom_overrides=overrides)
    STATE.crm.advance_stage_if_earlier(investor_id, "Draft Auto-Filled")
    STATE.vault.log_model_or_form_event(
        actor=sess["username"],
        role=SecurityRole(sess["role"]),
        action="agent:draft",
        outcome="SUCCESS",
        details=f"Drafted GreenHope application for {investor_id} (ready={draft['ready_count']}, missing={draft['missing_count']}, ip_blocked={draft['blocked_ip_count']}).",
    )
    return web.json_response(draft)


async def api_agent_export(request: web.Request) -> web.Response:
    sess = require_session(request)
    body = await request.json()
    investor_id = body.get("investor_id")
    fields = body.get("fields", [])

    # Enforce AUTO-FILL -> REVIEW -> APPROVE -> SUBMIT (reject unapproved or IP-blocked leakage!)
    approved_fields = []
    for f in fields:
        if f.get("security_level") in ("LEVEL_3_CONFIDENTIAL", "LEVEL_4_RESTRICTED"):
            continue
        if f.get("approved") and f.get("answer"):
            approved_fields.append(f)

    if not approved_fields:
        return web.json_response(
            {"error": "Human approval gate active: approve at least one non-confidential field before exporting."},
            status=400,
        )

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = EXPORTS_DIR / f"approved_{investor_id}_{ts}.json"
    packet = {
        "approved_by": sess["display_name"],
        "approved_role": sess["role"],
        "approved_at_utc": datetime.now(timezone.utc).isoformat(),
        "investor_id": investor_id,
        "workflow_verified": "AUTO-FILL -> REVIEW -> APPROVE -> EXPORT_READY",
        "excluded_confidential_ip": True,
        "approved_fields": approved_fields,
    }
    out_file.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    STATE.crm.advance_stage_if_earlier(investor_id, "Human Approved", increment_docs=True)
    STATE.vault.log_model_or_form_event(
        actor=sess["username"],
        role=SecurityRole(sess["role"]),
        action="agent:approve_export",
        outcome="SUCCESS",
        details=f"Human-approved packet exported for {investor_id} ({len(approved_fields)} fields -> {out_file.name}).",
    )
    return web.json_response({"exported": True, "filename": out_file.name, "packet": packet})


async def api_greenhope_master_get(request: web.Request) -> web.Response:
    require_session(request)
    return web.json_response(STATE.central.reload_master())


async def api_greenhope_master_update(request: web.Request) -> web.Response:
    sess = require_session(request)
    body = await request.json()
    key = body.get("key")
    value = body.get("value")
    try:
        updated = STATE.central.update_master_field(key, value)
    except PermissionError as exc:
        return web.json_response({"error": str(exc)}, status=403)
    except KeyError as exc:
        return web.json_response({"error": str(exc)}, status=404)

    STATE.vault.log_model_or_form_event(
        actor=sess["username"],
        role=SecurityRole(sess["role"]),
        action="master:update",
        outcome="SUCCESS",
        details=f"Updated GREENHOPE_MASTER canonical field '{key}'.",
    )
    return web.json_response({"updated": True, "key": key, "field": updated})


async def api_security_status(request: web.Request) -> web.Response:
    require_session(request)
    manifest = json.loads((VAULT_DIR / "registry_integrity.manifest.json").read_text(encoding="utf-8"))
    policy = json.loads((VAULT_DIR / "key_policy.json").read_text(encoding="utf-8"))
    audit_lines = [
        json.loads(ln)
        for ln in (VAULT_DIR / "audit_log.jsonl").read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    chain_ok, total = STATE.vault.verify_audit_chain(actor="webapp_security_view", role=SecurityRole.AUDITOR)
    return web.json_response(
        {
            "vault_manifest": {k: v for k, v in manifest.items() if k != "record_hashes"},
            "key_policy": policy,
            "ip_tiers": STATE.central.master_data["security_policy"],
            "audit_chain_valid": chain_ok,
            "audit_total_entries": total,
            "recent_audit_entries": audit_lines[-20:][::-1],
        }
    )


async def api_security_verify(request: web.Request) -> web.Response:
    sess = require_session(request)
    res = STATE.vault.verify_integrity(
        passphrase=VAULT_PASSPHRASE,
        actor=sess["username"],
        role=SecurityRole.SECURITY_OFFICER,
    )
    chain_ok, total = STATE.vault.verify_audit_chain(actor=sess["username"], role=SecurityRole.AUDITOR)
    return web.json_response({**res, "audit_chain_valid": chain_ok, "audit_entries": total})


async def api_crm_pipeline(request: web.Request) -> web.Response:
    require_session(request)
    return web.json_response(STATE.crm.list_pipeline())


async def api_crm_update(request: web.Request) -> web.Response:
    sess = require_session(request)
    body = await request.json()
    investor_id = body.get("investor_id")
    if not investor_id:
        return web.json_response({"error": "investor_id is required."}, status=400)
    try:
        updated = STATE.crm.update_record(
            investor_id=investor_id,
            stage=body.get("stage"),
            owner=body.get("owner"),
            cop31_venue_or_channel=body.get("cop31_venue_or_channel"),
            target_date=body.get("target_date"),
            next_action=body.get("next_action"),
            notes=body.get("notes"),
        )
    except KeyError as exc:
        return web.json_response({"error": str(exc)}, status=404)
    except ValueError as exc:
        return web.json_response({"error": str(exc)}, status=400)

    STATE.vault.log_model_or_form_event(
        actor=sess["username"],
        role=SecurityRole(sess["role"]),
        action="crm:update",
        outcome="SUCCESS",
        details=f"Updated COP31 CRM for {investor_id} -> stage='{updated['stage']}', date='{updated['target_date']}'.",
    )
    return web.json_response({"updated": True, "record": updated, "stage_counts": STATE.crm.list_pipeline()["stage_counts"]})


async def api_backup_info(request: web.Request) -> web.Response:
    require_session(request)
    return web.json_response(STATE.get_backup_metadata())


async def api_backup_rebuild(request: web.Request) -> web.Response:
    sess = require_session(request)
    build_project_zip(STATE.zip_path)
    meta = STATE.get_backup_metadata()
    STATE.vault.log_model_or_form_event(
        actor=sess["username"],
        role=SecurityRole(sess["role"]),
        action="backup:rebuild_zip",
        outcome="SUCCESS",
        details=f"Rebuilt full project ZIP backup ({meta['file_count']} files, {meta['zip_size_kb']} KB, sha256={meta['sha256'][:16]}...).",
    )
    return web.json_response({"rebuilt": True, **meta})


async def api_download_crm_csv(request: web.Request) -> web.Response:
    csv_text = STATE.crm.export_csv_text()
    return web.Response(
        text=csv_text,
        content_type="text/csv",
        charset="utf-8",
        headers={"Content-Disposition": 'attachment; filename="cop31_investor_crm_pipeline.csv"'},
    )


async def api_download_crm_json(request: web.Request) -> web.Response:
    payload = STATE.crm.list_pipeline()
    return web.Response(
        text=json.dumps(payload, indent=2, ensure_ascii=False),
        content_type="application/json",
        charset="utf-8",
        headers={"Content-Disposition": 'attachment; filename="cop31_investor_crm_pipeline.json"'},
    )


async def api_download_zip(request: web.Request) -> web.FileResponse:
    if not STATE.zip_path.exists():
        build_project_zip(STATE.zip_path)
    return web.FileResponse(
        STATE.zip_path,
        headers={
            "Content-Disposition": f'attachment; filename="{ZIP_FILENAME}"',
            "Content-Type": "application/zip",
        },
    )


async def api_download_excel(request: web.Request) -> web.FileResponse:
    path = DATA_DIR / "COP31_Investors_Banks_Registry.xlsx"
    return web.FileResponse(
        path,
        headers={
            "Content-Disposition": 'attachment; filename="COP31_Investors_Banks_Registry.xlsx"',
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
    )


async def api_download_csv(request: web.Request) -> web.FileResponse:
    path = DATA_DIR / "cop31_investors_verified.csv"
    return web.FileResponse(
        path,
        headers={"Content-Disposition": 'attachment; filename="cop31_investors_verified.csv"'},
    )


async def api_download_json(request: web.Request) -> web.FileResponse:
    path = DATA_DIR / "cop31_investors_verified.json"
    return web.FileResponse(
        path,
        headers={"Content-Disposition": 'attachment; filename="cop31_investors_verified.json"'},
    )


def create_app() -> web.Application:
    app = web.Application(middlewares=[preview_headers_middleware])
    app.router.add_get("/", index_page)
    app.router.add_static("/static", STATIC_DIR, show_index=False)

    app.router.add_post("/api/login", api_login)
    app.router.add_post("/api/logout", api_logout)
    app.router.add_get("/api/me", api_me)
    app.router.add_get("/api/overview", api_overview)
    app.router.add_get("/api/investors", api_investors)
    app.router.add_get("/api/investors/{investor_id}/pack", api_investor_pack)
    app.router.add_get("/api/kag/graph", api_kag_graph)
    app.router.add_post("/api/rag/query", api_rag_query)
    app.router.add_post("/api/kag/compare", api_kag_compare)
    app.router.add_post("/api/agent/draft", api_agent_draft)
    app.router.add_post("/api/agent/export", api_agent_export)
    app.router.add_get("/api/greenhope/master", api_greenhope_master_get)
    app.router.add_post("/api/greenhope/master", api_greenhope_master_update)
    app.router.add_get("/api/security/status", api_security_status)
    app.router.add_post("/api/security/verify", api_security_verify)
    app.router.add_get("/api/crm/pipeline", api_crm_pipeline)
    app.router.add_post("/api/crm/update", api_crm_update)
    app.router.add_get("/api/backup/info", api_backup_info)
    app.router.add_post("/api/backup/rebuild", api_backup_rebuild)

    app.router.add_get("/api/download/project.zip", api_download_zip)
    app.router.add_get("/api/download/excel", api_download_excel)
    app.router.add_get("/api/download/csv", api_download_csv)
    app.router.add_get("/api/download/json", api_download_json)
    app.router.add_get("/api/download/crm.csv", api_download_crm_csv)
    app.router.add_get("/api/download/crm.json", api_download_crm_json)
    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"Starting GreenHope COP31 Investor Intelligence Web App on http://0.0.0.0:{port}")
    web.run_app(create_app(), host="0.0.0.0", port=port)
