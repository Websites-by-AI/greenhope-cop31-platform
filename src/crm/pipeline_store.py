"""Persistent COP31 Investor Outreach & Application Tracking CRM / Pipeline Store.

Tracks all 66 verified COP31 entities across structured fundraising stages:
  Not Started -> Pack Ready -> Draft Auto-Filled -> Human Approved -> Submitted -> Meeting Booked -> Due Diligence / Partnered

Auto-syncs with the GreenHope Application Agent (drafting & human-approval exports)
and exports cleanly to CSV and JSON for offline reporting & backups.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models.schemas import InvestorRecord

PIPELINE_STAGES = [
    "Not Started",
    "Pack Ready",
    "Draft Auto-Filled",
    "Human Approved",
    "Submitted",
    "Meeting Booked",
    "Due Diligence / Partnered",
]

STAGE_RANK = {stage: idx for idx, stage in enumerate(PIPELINE_STAGES)}

# Pre-seeded realistic COP31 Antalya (Nov 9-20, 2026) action schedule for Top 10 P1 targets
DEFAULT_COP31_SEEDS: Dict[str, Dict[str, str]] = {
    "inv_bbva_group": {
        "stage": "Meeting Booked",
        "owner": "GreenHope Founder",
        "cop31_venue_or_channel": "Green Zone · BBVA 400 m² Climate Finance Hub Pavilion",
        "target_date": "2026-11-16",
        "next_action": "Present 1-page GreenHope City Pilot → Measurable Impact → Financing brief at BBVA Climate Finance Hub & Startup Zone Investor Lounge",
        "notes": "1st Priority Target (Global Banking Partner). Verified €700B sustainable target & innovation-to-investment clean-tech focus.",
    },
    "inv_aiib": {
        "stage": "Meeting Booked",
        "owner": "GreenHope Founder",
        "cop31_venue_or_channel": "COP31 Antalya · Nov 16 AIIB Program + AIIB–GGGI Project Prep",
        "target_date": "2026-11-16",
        "next_action": "Attend Nov 16 AIIB Antalya session; position GreenHope under AIIB–GGGI climate-resilient municipal project preparation pipeline",
        "notes": "2nd Priority Target. Fresh Nov 12 $1.6B Türkiye climate package + Nov 14 GGGI project-preparation cooperation.",
    },
    "inv_world_bank_ibrd": {
        "stage": "Draft Auto-Filled",
        "owner": "GreenHope Founder",
        "cop31_venue_or_channel": "Blue Zone · Joint MDB Pavilion / Global Finance Summit",
        "target_date": "2026-11-17",
        "next_action": "Ask WBG / IFC urban resilience team which municipal intermediary, guarantee, or IFC private-sector window fits GreenHope pilot",
        "notes": "3rd Priority Target. Focus on country urban resilience programs & MIGA/IFC de-risking rather than raw grant ask.",
    },
    "inv_garanti_bbva": {
        "stage": "Draft Auto-Filled",
        "owner": "Türkiye Partnerships Lead",
        "cop31_venue_or_channel": "Green Zone · BBVA / Garanti BBVA Climate Finance Hub",
        "target_date": "2026-11-16",
        "next_action": "Confirm Türkiye domestic green credit / SME / municipal pilot co-financing channel alongside BBVA Group",
        "notes": "TRY 3.5T 2029 sustainable finance target; strongest local banking bridge in Antalya.",
    },
    "inv_qnb_turkiye": {
        "stage": "Pack Ready",
        "owner": "Türkiye Partnerships Lead",
        "cop31_venue_or_channel": "COP31 Business Forum · Climate Finance WG",
        "target_date": "2026-11-17",
        "next_action": "Review QNB Türkiye $500M COP31 green credit + Proparco €75M leasing eligibility for GreenHope hardware/sensors",
        "notes": "Fast commercial execution for Türkiye pilot equipment & corporate climate-tech partners.",
    },
    "inv_meridiam": {
        "stage": "Pack Ready",
        "owner": "Infrastructure Finance Lead",
        "cop31_venue_or_channel": "COP31 Business Forum · Infrastructure & Resilience Track",
        "target_date": "2026-11-18",
        "next_action": "Pitch municipal urban-resilience & waste/air-quality PPP scaling pathway once city pilot KPIs are validated",
        "notes": "Strong long-term urban infrastructure equity investor for Phase 2 municipal scale-up.",
    },
    "inv_m_and_g": {
        "stage": "Pack Ready",
        "owner": "Institutional IR Lead",
        "cop31_venue_or_channel": "COP31 Business Forum · Climate Finance WG",
        "target_date": "2026-11-18",
        "next_action": "Introduce GreenHope Impact & MRV verification data layer to M&G Catalyst / impact strategies",
        "notes": "Institutional asset manager active in COP31 Climate Finance WG.",
    },
    "inv_hsbc": {
        "stage": "Pack Ready",
        "owner": "Institutional IR Lead",
        "cop31_venue_or_channel": "COP31 Business Forum / GFANZ Transition Track",
        "target_date": "2026-11-18",
        "next_action": "Explore HSBC Climate Tech / global transition finance corridor for multi-city replication",
        "notes": "Global transition finance bank; relevant for cross-border expansion beyond Türkiye.",
    },
    "inv_akbank": {
        "stage": "Pack Ready",
        "owner": "Türkiye Partnerships Lead",
        "cop31_venue_or_channel": "COP31 Green Zone · Turkish Banking Pavilions",
        "target_date": "2026-11-17",
        "next_action": "Verify Akbank TRY 2.5T sustainable finance & GEFF green technology lending eligibility",
        "notes": "Strong digital/green banking innovation alignment in Türkiye.",
    },
    "inv_denizbank": {
        "stage": "Pack Ready",
        "owner": "Türkiye Partnerships Lead",
        "cop31_venue_or_channel": "COP31 Business Forum · Climate Finance WG",
        "target_date": "2026-11-18",
        "next_action": "Map DenizBank agri-climate & regional Anatolian municipal/SME pilot channels",
        "notes": "Active COP31 Climate Finance WG Turkish bank with strong Antalya/Mediterranean regional presence.",
    },
    "inv_ebrd": {
        "stage": "Pack Ready",
        "owner": "MDB Relations Lead",
        "cop31_venue_or_channel": "Blue Zone · Joint MDB Pavilion (EBRD Green Cities)",
        "target_date": "2026-11-17",
        "next_action": "Align GreenHope city resilience & MRV layer with EBRD Green Cities & Türkiye GEFF frameworks",
        "notes": ">€26B cumulative Türkiye portfolio; top MDB match for municipal & industrial pilots.",
    },
    "inv_gggi": {
        "stage": "Meeting Booked",
        "owner": "GreenHope Founder",
        "cop31_venue_or_channel": "COP31 Antalya · AIIB–GGGI Cooperation Track",
        "target_date": "2026-11-16",
        "next_action": "Connect with GGGI project-preparation team to structure bankable municipal pilot under Nov 14 AIIB–GGGI agreement",
        "notes": "Strategic project-preparation & technical assistance bridge into AIIB/GCF financing.",
    },
}


class InvestorCRMPipeline:
    """Manages persistent CRM pipeline state for all 66 verified COP31 entities."""

    def __init__(self, store_path: Path, investors: List[InvestorRecord]) -> None:
        self.store_path = Path(store_path)
        self.investors = investors
        self.by_id: Dict[str, InvestorRecord] = {inv.investor_id: inv for inv in investors}
        self.records: Dict[str, Dict[str, Any]] = {}
        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        existing: Dict[str, Dict[str, Any]] = {}
        if self.store_path.exists():
            try:
                raw = json.loads(self.store_path.read_text(encoding="utf-8"))
                existing = raw.get("records", {})
            except Exception:
                existing = {}

        changed = not self.store_path.exists()
        for inv in self.investors:
            iid = inv.investor_id
            if iid in existing:
                self.records[iid] = existing[iid]
                continue

            seed = DEFAULT_COP31_SEEDS.get(iid)
            if seed:
                self.records[iid] = {
                    "investor_id": iid,
                    "stage": seed["stage"],
                    "owner": seed["owner"],
                    "cop31_venue_or_channel": seed["cop31_venue_or_channel"],
                    "target_date": seed["target_date"],
                    "next_action": seed["next_action"],
                    "notes": seed["notes"],
                    "submitted_docs_count": 0,
                    "last_updated_utc": now,
                }
            else:
                default_stage = "Pack Ready" if inv.knowledge_pack_slug else "Not Started"
                default_venue = (
                    "Green Zone · COP31 Startup Zone / Investor Lounge"
                    if "Tier A" in inv.priority_tier
                    else ("COP31 Business Forum · Climate Finance WG" if "Tier B" in inv.priority_tier else "COP31 Partner / Ecosystem Track")
                )
                self.records[iid] = {
                    "investor_id": iid,
                    "stage": default_stage,
                    "owner": "GreenHope Team",
                    "cop31_venue_or_channel": default_venue,
                    "target_date": "2026-11-19" if "Tier B" in inv.priority_tier else "2026-11-20",
                    "next_action": f"Review {inv.short_name} COP31 mandate ({inv.relationship_status.value}) and decide outreach sequence.",
                    "notes": inv.greenhope_fit_notes,
                    "submitted_docs_count": 0,
                    "last_updated_utc": now,
                }
            changed = True

        if changed:
            self._save()

    def _save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": "1.0",
            "stages": PIPELINE_STAGES,
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_entities": len(self.records),
            "records": self.records,
        }
        self.store_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def list_pipeline(self) -> Dict[str, Any]:
        stage_counts = {s: 0 for s in PIPELINE_STAGES}
        enriched: List[Dict[str, Any]] = []

        for inv in self.investors:
            rec = self.records[inv.investor_id]
            st = rec.get("stage", "Not Started")
            stage_counts[st] = stage_counts.get(st, 0) + 1
            enriched.append(
                {
                    **rec,
                    "name": inv.name,
                    "short_name": inv.short_name,
                    "relationship_status": inv.relationship_status.value,
                    "priority_tier": inv.priority_tier,
                    "ai_rag_priority": inv.ai_rag_priority,
                    "ecosystem_branch": inv.ecosystem_branch.value,
                    "has_pack": bool(inv.knowledge_pack_slug),
                    "portal_url": inv.application_portal_url,
                }
            )

        # Sort active/advanced deals & P1 targets to the top
        enriched.sort(
            key=lambda x: (
                -STAGE_RANK.get(x["stage"], 0),
                0 if x["ai_rag_priority"] == "P1" else (1 if x["ai_rag_priority"] == "P2" else 2),
                x["short_name"].lower(),
            )
        )
        return {
            "stages": PIPELINE_STAGES,
            "stage_counts": stage_counts,
            "total": len(enriched),
            "items": enriched,
        }

    def update_record(
        self,
        investor_id: str,
        stage: Optional[str] = None,
        owner: Optional[str] = None,
        cop31_venue_or_channel: Optional[str] = None,
        target_date: Optional[str] = None,
        next_action: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        if investor_id not in self.records:
            raise KeyError(f"Unknown investor_id: {investor_id}")
        rec = self.records[investor_id]

        if stage is not None:
            if stage not in PIPELINE_STAGES:
                raise ValueError(f"Invalid stage '{stage}'. Valid stages: {PIPELINE_STAGES}")
            rec["stage"] = stage
        if owner is not None:
            rec["owner"] = str(owner).strip()
        if cop31_venue_or_channel is not None:
            rec["cop31_venue_or_channel"] = str(cop31_venue_or_channel).strip()
        if target_date is not None:
            rec["target_date"] = str(target_date).strip()
        if next_action is not None:
            rec["next_action"] = str(next_action).strip()
        if notes is not None:
            rec["notes"] = str(notes).strip()

        rec["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return rec

    def advance_stage_if_earlier(self, investor_id: str, min_stage: str, increment_docs: bool = False) -> Dict[str, Any]:
        """Auto-advance CRM stage when the Application Agent drafts or exports a human-approved packet."""
        if investor_id not in self.records or min_stage not in STAGE_RANK:
            return {}
        rec = self.records[investor_id]
        cur_rank = STAGE_RANK.get(rec.get("stage", "Not Started"), 0)
        if STAGE_RANK[min_stage] > cur_rank:
            rec["stage"] = min_stage
        if increment_docs:
            rec["submitted_docs_count"] = int(rec.get("submitted_docs_count", 0)) + 1
        rec["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return rec

    def export_csv_text(self) -> str:
        data = self.list_pipeline()["items"]
        buf = io.StringIO()
        fields = [
            "investor_id",
            "name",
            "relationship_status",
            "priority_tier",
            "ai_rag_priority",
            "stage",
            "owner",
            "target_date",
            "cop31_venue_or_channel",
            "next_action",
            "submitted_docs_count",
            "notes",
            "last_updated_utc",
        ]
        writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return buf.getvalue()
