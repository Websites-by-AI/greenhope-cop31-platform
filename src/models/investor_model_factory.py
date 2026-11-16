"""Step 2: Per-Investor KAG/RAG AI Model Factory.

Strictly enforces the two-step workflow requested by the user:
  Step 1: Verify and decrypt the secured COP31 investor list from `InvestorSecurityVault`.
  Step 2: For EACH verified investor, create a tenant-isolated KAG, RAG, or HYBRID_KAG_RAG model
          with its own Knowledge Graph, RAG corpus, form schema, HKDF subkey fingerprint, and signed artifact manifest.
"""

from __future__ import annotations

import hmac
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..forms.form_templates import get_form_template
from ..security.crypto_engine import sha256_hex
from ..security.tenant_guard import TenantIsolationGuard
from ..security.vault import InvestorSecurityVault, VaultIntegrityError
from .hybrid_kag_rag import InvestorHybridKAGRAGEngine
from .kag_engine import InvestorKAGEngine
from .llm_adapter import GroundedLLMAdapter
from .rag_engine import InvestorRAGEngine
from .schemas import (
    AIModelArchitecture,
    InvestorModelManifest,
    InvestorRecord,
    SecurityRole,
)

AnyInvestorEngine = Union[InvestorKAGEngine, InvestorRAGEngine, InvestorHybridKAGRAGEngine]


class PerInvestorModelFactory:
    """Creates, isolates, verifies, and loads dedicated KAG/RAG AI models for every COP31 investor."""

    def __init__(self, vault: InvestorSecurityVault, models_root: Path) -> None:
        self.vault = vault
        self.models_root = Path(models_root)
        self.models_root.mkdir(parents=True, exist_ok=True)
        self.catalog_path = self.models_root / "model_catalog.json"

    def build_all_models_from_secured_vault(
        self,
        passphrase: str,
        actor: str = "model_engineer",
        role: SecurityRole = SecurityRole.MODEL_ENGINEER,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> List[InvestorModelManifest]:
        """Step 2 entry point: decrypt Step 1 vault and build an isolated KAG/RAG/Hybrid model per investor."""
        # RBAC check for model:build
        self.vault._authorize(actor, role, "model:build")

        # Step 1 verification & decryption (raises VaultIntegrityError if anything was tampered)
        investors, master_key, tenant_salt, record_hashes = self.vault.load_verified_investors(
            passphrase=passphrase,
            actor=actor,
            role=role,
        )

        manifests: List[InvestorModelManifest] = []
        for investor in investors:
            manifest = self._build_single_investor_model(
                investor=investor,
                master_key=master_key,
                tenant_salt=tenant_salt,
                source_record_hash=record_hashes[investor.investor_id],
                llm_adapter=llm_adapter,
            )
            manifests.append(manifest)

        # Save master catalog of all created per-investor models
        summary = {
            "total_models_created": len(manifests),
            "architecture_breakdown": {
                arch.value: sum(1 for m in manifests if m.model_architecture == arch)
                for arch in AIModelArchitecture
            },
            "models": [m.model_dump(mode="json") for m in manifests],
        }
        self.catalog_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

        self.vault.log_model_or_form_event(
            actor=actor,
            role=role,
            action="model:build",
            outcome="SUCCESS",
            details=(
                f"Built {len(manifests)} isolated per-investor AI models "
                f"(KAG={summary['architecture_breakdown']['KAG']}, "
                f"RAG={summary['architecture_breakdown']['RAG']}, "
                f"HYBRID={summary['architecture_breakdown']['HYBRID_KAG_RAG']})."
            ),
        )
        return manifests

    def _build_single_investor_model(
        self,
        investor: InvestorRecord,
        master_key: bytes,
        tenant_salt: bytes,
        source_record_hash: str,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> InvestorModelManifest:
        guard = TenantIsolationGuard(
            models_root=self.models_root,
            investor_id=investor.investor_id,
            master_key=master_key,
            tenant_salt=tenant_salt,
        )
        guard.tenant_dir.mkdir(parents=True, exist_ok=True)

        arch = investor.recommended_ai_model_type
        artifact_hashes: Dict[str, str] = {}

        # Always persist the investor's dedicated form schema inside its tenant directory
        template = get_form_template(investor.form_template_type)
        form_schema_path = guard.assert_path_within_tenant(guard.tenant_dir / "form_schema.json")
        form_schema_payload = {
            "investor_id": investor.investor_id,
            "investor_name": investor.name,
            "portal_url": investor.application_portal_url,
            "template": template.model_dump(mode="json"),
        }
        form_schema_path.write_text(json.dumps(form_schema_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        artifact_hashes["form_schema.json"] = sha256_hex(form_schema_path.read_bytes())

        has_kag = arch in {AIModelArchitecture.KAG, AIModelArchitecture.HYBRID_KAG_RAG}
        has_rag = arch in {AIModelArchitecture.RAG, AIModelArchitecture.HYBRID_KAG_RAG}
        kag_nodes = 0
        kag_edges = 0
        rag_chunks = 0

        if has_kag:
            kag = InvestorKAGEngine.build_for_investor(investor, tenant_guard=guard, llm_adapter=llm_adapter)
            kg_path = guard.assert_path_within_tenant(guard.tenant_dir / "knowledge_graph.json")
            kag.save(kg_path)
            kag_nodes = kag.graph.number_of_nodes()
            kag_edges = kag.graph.number_of_edges()
            artifact_hashes["knowledge_graph.json"] = sha256_hex(kg_path.read_bytes())

        if has_rag:
            rag = InvestorRAGEngine.build_for_investor(investor, tenant_guard=guard, llm_adapter=llm_adapter)
            rag_path = guard.assert_path_within_tenant(guard.tenant_dir / "rag_corpus.json")
            rag.save(rag_path)
            rag_chunks = len(rag.chunks)
            artifact_hashes["rag_corpus.json"] = sha256_hex(rag_path.read_bytes())

        manifest = InvestorModelManifest(
            investor_id=investor.investor_id,
            investor_name=investor.name,
            short_name=investor.short_name,
            category=investor.category,
            model_architecture=arch,
            ai_model_rationale=investor.ai_model_rationale,
            form_template_type=investor.form_template_type,
            tenant_namespace=guard.namespace,
            tenant_key_fingerprint=guard.subkey_fingerprint,
            source_record_sha256=source_record_hash,
            has_kag_graph=has_kag,
            has_rag_corpus=has_rag,
            kag_nodes_count=kag_nodes,
            kag_edges_count=kag_edges,
            rag_chunks_count=rag_chunks,
            artifact_hashes=artifact_hashes,
        )
        manifest_path = guard.assert_path_within_tenant(guard.tenant_dir / "model_manifest.json")
        manifest_path.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")
        return manifest

    def load_investor_model(
        self,
        investor: InvestorRecord,
        master_key: bytes,
        tenant_salt: bytes,
        llm_adapter: Optional[GroundedLLMAdapter] = None,
    ) -> Tuple[AnyInvestorEngine, InvestorModelManifest, TenantIsolationGuard]:
        """Load and integrity-verify a single investor's isolated KAG, RAG, or Hybrid model."""
        guard = TenantIsolationGuard(
            models_root=self.models_root,
            investor_id=investor.investor_id,
            master_key=master_key,
            tenant_salt=tenant_salt,
        )
        manifest_path = guard.assert_path_within_tenant(guard.tenant_dir / "model_manifest.json")
        if not manifest_path.exists():
            raise FileNotFoundError(f"Model for {investor.investor_id} not yet built. Run Step 2 build first.")

        manifest = InvestorModelManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
        guard.assert_investor_match(manifest.investor_id)

        if not hmac.compare_digest(manifest.tenant_key_fingerprint, guard.subkey_fingerprint):
            raise VaultIntegrityError(
                f"Tenant key fingerprint mismatch for {investor.investor_id}: possible cross-vault or key tamper!"
            )

        # Verify every model artifact SHA-256 against manifest before loading into memory
        for filename, expected_hash in manifest.artifact_hashes.items():
            fpath = guard.assert_path_within_tenant(guard.tenant_dir / filename)
            actual_hash = sha256_hex(fpath.read_bytes())
            if not hmac.compare_digest(actual_hash, expected_hash):
                raise VaultIntegrityError(
                    f"Tampering detected in model artifact '{filename}' for tenant '{investor.investor_id}'!"
                )

        if manifest.model_architecture == AIModelArchitecture.KAG:
            kag = InvestorKAGEngine.load(
                investor=investor,
                path=guard.tenant_dir / "knowledge_graph.json",
                tenant_guard=guard,
                llm_adapter=llm_adapter,
            )
            return kag, manifest, guard

        if manifest.model_architecture == AIModelArchitecture.RAG:
            rag = InvestorRAGEngine.load(
                investor=investor,
                path=guard.tenant_dir / "rag_corpus.json",
                tenant_guard=guard,
                llm_adapter=llm_adapter,
            )
            return rag, manifest, guard

        # HYBRID_KAG_RAG
        kag = InvestorKAGEngine.load(
            investor=investor,
            path=guard.tenant_dir / "knowledge_graph.json",
            tenant_guard=guard,
            llm_adapter=llm_adapter,
        )
        rag = InvestorRAGEngine.load(
            investor=investor,
            path=guard.tenant_dir / "rag_corpus.json",
            tenant_guard=guard,
            llm_adapter=llm_adapter,
        )
        hybrid = InvestorHybridKAGRAGEngine(
            investor=investor,
            kag=kag,
            rag=rag,
            tenant_guard=guard,
            llm_adapter=llm_adapter,
        )
        return hybrid, manifest, guard
