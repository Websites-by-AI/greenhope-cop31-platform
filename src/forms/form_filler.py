"""Step 3: Automated Per-Investor Form-Filling Pipeline.

Workflow:
1. Decrypt & verify the secured COP31 investor list (Step 1 RBAC + AES-256-GCM + Merkle check).
2. Redact sensitive applicant PII from free-text narratives before AI model execution.
3. Screen & rank all 40 COP31 investors using each investor's isolated KAG/RAG/Hybrid model.
4. Auto-fill EVERY field of a target investor's official form schema with provenance traces,
   confidence scores, compliance warnings, and a pre-submission checklist.
5. Export decision-ready JSON and formatted Markdown submission packets.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.investor_model_factory import PerInvestorModelFactory
from ..models.llm_adapter import GroundedLLMAdapter
from ..models.schemas import (
    ApplicantProject,
    EligibilityEvaluation,
    FieldFillStatus,
    FilledApplicationPacket,
    InvestorRecord,
    SecurityRole,
)
from ..security.tenant_guard import PIIRedactor
from ..security.vault import InvestorSecurityVault
from .form_templates import get_form_template


class COP31FormFiller:
    """Orchestrates secured investor matching and per-investor KAG/RAG form completion."""

    def __init__(
        self,
        vault: InvestorSecurityVault,
        model_factory: PerInvestorModelFactory,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> None:
        self.vault = vault
        self.factory = model_factory
        self.llm = llm_adapter or GroundedLLMAdapter()

    @staticmethod
    def _sanitize_project_for_ai(project: ApplicantProject) -> ApplicantProject:
        """Redact emails, IBANs, tax IDs, and phone numbers from free-text fields before AI inference."""
        data = project.model_dump()
        for key in [
            "project_summary",
            "climate_rationale",
            "technology_and_innovation",
            "esg_and_social_impact",
            "key_risks_and_mitigants",
        ]:
            if isinstance(data.get(key), str):
                sanitized, _ = PIIRedactor.redact_text(data[key])
                data[key] = sanitized
        return ApplicantProject.model_validate(data)

    def rank_matching_investors(
        self,
        project: ApplicantProject,
        passphrase: str,
        top_n: int = 10,
        actor: str = "form_operator",
        role: SecurityRole = SecurityRole.FORM_OPERATOR,
    ) -> List[Tuple[InvestorRecord, EligibilityEvaluation]]:
        """Evaluate applicant fit across ALL 40 isolated per-investor KAG/RAG models and rank best matches."""
        self.vault._authorize(actor, role, "form:fill")
        investors, master_key, tenant_salt, _ = self.vault.load_verified_investors(
            passphrase=passphrase,
            actor=actor,
            role=role,
        )
        safe_project = self._sanitize_project_for_ai(project)

        scored: List[Tuple[InvestorRecord, EligibilityEvaluation]] = []
        for inv in investors:
            engine, _, _ = self.factory.load_investor_model(
                investor=inv,
                master_key=master_key,
                tenant_salt=tenant_salt,
                llm_adapter=self.llm,
            )
            evaluation = engine.evaluate_eligibility(safe_project)
            scored.append((inv, evaluation))

        scored.sort(key=lambda item: (item[1].eligible, item[1].fit_score), reverse=True)
        self.vault.log_model_or_form_event(
            actor=actor,
            role=role,
            action="form:match",
            outcome="SUCCESS",
            details=f"Screened {len(scored)} COP31 investors for project '{project.project_id}'; top match={scored[0][0].investor_id} ({scored[0][1].fit_score}).",
        )
        return scored[:top_n]

    def fill_investor_form(
        self,
        investor_id: str,
        project: ApplicantProject,
        passphrase: str,
        actor: str = "form_operator",
        role: SecurityRole = SecurityRole.FORM_OPERATOR,
    ) -> FilledApplicationPacket:
        """Auto-fill a specific investor's form using ONLY that investor's tenant-isolated KAG/RAG/Hybrid model."""
        self.vault._authorize(actor, role, "form:fill")
        investors, master_key, tenant_salt, _ = self.vault.load_verified_investors(
            passphrase=passphrase,
            actor=actor,
            role=role,
        )
        inv_map: Dict[str, InvestorRecord] = {inv.investor_id: inv for inv in investors}
        if investor_id not in inv_map:
            raise KeyError(f"Investor '{investor_id}' not found in verified COP31 vault.")

        investor = inv_map[investor_id]
        safe_project = self._sanitize_project_for_ai(project)

        engine, manifest, guard = self.factory.load_investor_model(
            investor=investor,
            master_key=master_key,
            tenant_salt=tenant_salt,
            llm_adapter=self.llm,
        )
        guard.assert_investor_match(investor.investor_id)

        eligibility = engine.evaluate_eligibility(safe_project)
        template = get_form_template(investor.form_template_type)

        filled_fields = [
            engine.fill_field(field=f, project=safe_project, eligibility=eligibility)
            for f in template.fields
        ]

        filled_count = sum(1 for ff in filled_fields if ff.status == FieldFillStatus.FILLED)
        partial_count = sum(1 for ff in filled_fields if ff.status == FieldFillStatus.PARTIAL_NEEDS_REVIEW)
        completion_rate = round(((filled_count + 0.5 * partial_count) / max(1, len(filled_fields))) * 100.0, 1)
        avg_conf = round(sum(ff.confidence for ff in filled_fields) / max(1, len(filled_fields)), 3)

        checklist: List[str] = []
        for req in investor.mandatory_form_requirements:
            checklist.append(f"[Mandatory Requirement] {req}")
        for warn in eligibility.warnings:
            checklist.append(f"[Screening Warning] {warn}")
        for ff in filled_fields:
            if ff.status != FieldFillStatus.FILLED:
                checklist.append(f"[Field Review: {ff.label}] Status={ff.status.value} — {'; '.join(ff.compliance_notes) or 'Verify prior to submission'}")
        checklist.append(f"[Portal Submission] Upload finalized packet via official portal: {investor.application_portal_url}")

        packet = FilledApplicationPacket(
            submission_id=f"sub_{investor.investor_id}_{project.project_id}_{uuid.uuid4().hex[:8]}",
            investor_id=investor.investor_id,
            investor_name=investor.name,
            model_architecture=manifest.model_architecture,
            form_template_id=template.template_id,
            form_title=template.title,
            project_id=project.project_id,
            project_title=project.project_title,
            pii_redacted_for_ai_context=True,
            tenant_isolation_verified=True,
            eligibility=eligibility,
            completion_rate_percent=completion_rate,
            average_confidence=avg_conf,
            fields=filled_fields,
            pre_submission_checklist=checklist,
            llm_backend_used=self.llm.backend_label,
        )

        self.vault.log_model_or_form_event(
            actor=actor,
            role=role,
            action="form:fill",
            outcome="SUCCESS",
            details=(
                f"Auto-filled '{template.template_id.value}' for {investor.investor_id} "
                f"using {manifest.model_architecture.value} (project={project.project_id}, "
                f"fit={eligibility.fit_score}, completion={completion_rate}%)."
            ),
        )
        return packet

    @staticmethod
    def export_packet(packet: FilledApplicationPacket, output_dir: Path) -> Tuple[Path, Path]:
        """Save filled form packet as structured JSON and clean human-readable Markdown."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        base = f"{packet.investor_id}__{packet.project_id}"
        json_path = output_dir / f"{base}.filled_form.json"
        md_path = output_dir / f"{base}.filled_form.md"

        json_path.write_text(json.dumps(packet.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")

        lines: List[str] = [
            f"# Auto-Filled COP31 Investor Application Packet",
            "",
            f"- **Submission ID:** `{packet.submission_id}`",
            f"- **Target Investor / Bank:** {packet.investor_name} (`{packet.investor_id}`)",
            f"- **AI Model Architecture:** `{packet.model_architecture.value}`",
            f"- **Form Template:** {packet.form_title} (`{packet.form_template_id.value}`)",
            f"- **Applicant Project:** {packet.project_title} (`{packet.project_id}`)",
            f"- **Security Controls:** Tenant Isolation Verified=`{packet.tenant_isolation_verified}` | PII Redacted=`{packet.pii_redacted_for_ai_context}`",
            f"- **Eligibility Decision:** `{'ELIGIBLE' if packet.eligibility.eligible else 'CONDITIONAL / REVIEW'}` (Fit Score: **{packet.eligibility.fit_score}/100**, Recommended Instrument: **{packet.eligibility.recommended_instrument}**)",
            f"- **Completion Rate:** **{packet.completion_rate_percent}%** | **Average Confidence:** **{packet.average_confidence:.2f}**",
            f"- **Synthesis Backend:** `{packet.llm_backend_used}`",
            "",
            "## Eligibility Screening Summary",
            "",
        ]
        for chk in packet.eligibility.passed_checks:
            lines.append(f"- [PASS] {chk}")
        for warn in packet.eligibility.warnings:
            lines.append(f"- [WARN] {warn}")
        for fail in packet.eligibility.failed_checks:
            lines.append(f"- [FAIL] {fail}")

        lines.extend(["", "## Auto-Filled Form Fields", ""])
        current_section = ""
        for ff in packet.fields:
            if ff.section != current_section:
                current_section = ff.section
                lines.extend([f"### {current_section}", ""])
            lines.append(f"**{ff.label}** (`{ff.field_id}`) — Status: `{ff.status.value}` | Confidence: `{ff.confidence:.2f}` | Mode: `{ff.reasoning_mode}`")
            lines.append(f"> {ff.value}")
            if ff.kag_reasoning_path:
                lines.append(f"- *KAG Trace:* `{ff.kag_reasoning_path}`")
            if ff.rag_citations:
                lines.append(f"- *RAG Citations:* {', '.join(f'`{c}`' for c in ff.rag_citations)}")
            if ff.compliance_notes:
                lines.append(f"- *Compliance Notes:* {' | '.join(ff.compliance_notes)}")
            lines.append("")

        lines.extend(["## Pre-Submission Human & Compliance Checklist", ""])
        for item in packet.pre_submission_checklist:
            lines.append(f"- [ ] {item}")
        lines.append("")

        md_path.write_text("\n".join(lines), encoding="utf-8")
        return json_path, md_path
