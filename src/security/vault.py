"""Step 1: COP31 Investor Registry Security Vault.

Provides:
1. Schema & provenance validation of the verified COP31 investor/bank list.
2. AES-256-GCM encryption at rest with PBKDF2-HMAC-SHA256 master key derivation.
3. Per-record SHA-256 hashes + Merkle root + HMAC-SHA256 manifest signature to detect tampering.
4. Role-Based Access Control (RBAC) enforcing least-privilege operations.
5. Tamper-evident SHA-256 hash-chained audit trail (`audit_log.jsonl`).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.schemas import InvestorRecord, SecurityRole
from .crypto_engine import (
    PBKDF2_ITERATIONS,
    backend_name,
    decrypt_aes256_gcm,
    derive_master_key,
    encrypt_aes256_gcm,
    generate_salt,
    hmac_sha256_hex,
    key_fingerprint,
    sha256_hex,
)

VAULT_AAD = b"cop31-antalya-2026-investor-registry-vault-v1"

ROLE_PERMISSIONS: Dict[SecurityRole, set[str]] = {
    SecurityRole.ADMIN: {"vault:seal", "vault:read", "vault:verify", "model:build", "form:fill", "audit:read"},
    SecurityRole.SECURITY_OFFICER: {"vault:seal", "vault:verify", "audit:read"},
    SecurityRole.MODEL_ENGINEER: {"vault:read", "vault:verify", "model:build"},
    SecurityRole.FORM_OPERATOR: {"vault:read", "vault:verify", "form:fill"},
    SecurityRole.AUDITOR: {"vault:verify", "audit:read"},
}


class AccessDeniedError(PermissionError):
    """Raised when an actor's SecurityRole lacks the required permission."""


class VaultIntegrityError(ValueError):
    """Raised when registry hashes, Merkle root, manifest HMAC, or audit chain verification fails."""


def compute_merkle_root(hex_hashes: List[str]) -> str:
    """Compute a deterministic SHA-256 Merkle root over sorted record hashes."""
    if not hex_hashes:
        return sha256_hex(b"EMPTY_REGISTRY")
    layer = sorted(hex_hashes)
    while len(layer) > 1:
        next_layer: List[str] = []
        for idx in range(0, len(layer), 2):
            left = layer[idx]
            right = layer[idx + 1] if idx + 1 < len(layer) else left
            next_layer.append(sha256_hex((left + right).encode("ascii")))
        layer = next_layer
    return layer[0]


def canonical_record_hash(record: InvestorRecord) -> str:
    """Deterministic SHA-256 hash of a validated InvestorRecord."""
    payload = json.dumps(record.model_dump(mode="json"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return sha256_hex(payload)


class InvestorSecurityVault:
    """Secures and governs access to the verified COP31 investor & bank registry."""

    def __init__(self, vault_dir: Path) -> None:
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.encrypted_file = self.vault_dir / "cop31_investors.vault.enc"
        self.manifest_file = self.vault_dir / "registry_integrity.manifest.json"
        self.policy_file = self.vault_dir / "key_policy.json"
        self.audit_file = self.vault_dir / "audit_log.jsonl"

    def _authorize(self, actor: str, role: SecurityRole, permission: str, details: str = "") -> None:
        allowed = permission in ROLE_PERMISSIONS.get(role, set())
        if not allowed:
            self._append_audit(
                actor=actor,
                role=role.value,
                action=permission,
                outcome="DENIED",
                details=details or f"Role {role.value} lacks permission {permission}",
            )
            raise AccessDeniedError(f"Actor '{actor}' with role '{role.value}' is not permitted to perform '{permission}'.")

    def _append_audit(self, actor: str, role: str, action: str, outcome: str, details: str) -> dict:
        prev_hash = "GENESIS_COP31_AUDIT_CHAIN"
        if self.audit_file.exists():
            lines = [ln for ln in self.audit_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if lines:
                prev_hash = json.loads(lines[-1])["entry_hash"]

        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "role": role,
            "action": action,
            "outcome": outcome,
            "details": details,
            "prev_hash": prev_hash,
        }
        canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
        entry["entry_hash"] = sha256_hex(canonical)

        with self.audit_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def verify_audit_chain(self, actor: str = "system", role: SecurityRole = SecurityRole.AUDITOR) -> Tuple[bool, int]:
        """Verify that no audit log entry has been altered or deleted."""
        self._authorize(actor, role, "audit:read")
        if not self.audit_file.exists():
            return True, 0
        lines = [ln for ln in self.audit_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
        expected_prev = "GENESIS_COP31_AUDIT_CHAIN"
        for idx, line in enumerate(lines):
            entry = json.loads(line)
            if entry.get("prev_hash") != expected_prev:
                raise VaultIntegrityError(f"Audit log chain broken at line {idx + 1}: prev_hash mismatch.")
            recorded_hash = entry.pop("entry_hash", None)
            recomputed = sha256_hex(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8"))
            if not recorded_hash or not hmac.compare_digest(recorded_hash, recomputed):
                raise VaultIntegrityError(f"Audit log entry tampered at line {idx + 1}.")
            expected_prev = recorded_hash
        return True, len(lines)

    def seal_registry(
        self,
        investors: List[InvestorRecord],
        passphrase: str,
        actor: str = "security_admin",
        role: SecurityRole = SecurityRole.ADMIN,
    ) -> dict:
        """Validate, hash, sign, and encrypt the verified COP31 investor list into the security vault."""
        self._authorize(actor, role, "vault:seal")
        if not investors:
            raise VaultIntegrityError("Cannot seal an empty investor registry.")

        # Ensure unique investor IDs and valid Pydantic models
        seen_ids = set()
        record_hashes: Dict[str, str] = {}
        serialized_records: List[dict] = []
        for inv in investors:
            validated = InvestorRecord.model_validate(inv)
            if validated.investor_id in seen_ids:
                raise VaultIntegrityError(f"Duplicate investor_id detected: {validated.investor_id}")
            seen_ids.add(validated.investor_id)
            record_hashes[validated.investor_id] = canonical_record_hash(validated)
            serialized_records.append(validated.model_dump(mode="json"))

        merkle_root = compute_merkle_root(list(record_hashes.values()))
        master_salt = generate_salt(16)
        tenant_salt = generate_salt(16)
        master_key = derive_master_key(passphrase, master_salt)

        plaintext = json.dumps(
            {
                "schema_version": "1.0.0",
                "summit": "UNFCCC COP31 Antalya, Türkiye (9-20 November 2026)",
                "record_count": len(serialized_records),
                "merkle_root": merkle_root,
                "investors": serialized_records,
            },
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")

        encrypted_envelope = encrypt_aes256_gcm(master_key, plaintext, aad=VAULT_AAD)
        vault_payload = {
            "vault_format": "COP31-SECURED-VAULT-V1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "kdf": {
                "algorithm": "PBKDF2-HMAC-SHA256",
                "iterations": PBKDF2_ITERATIONS,
                "master_salt_b64": base64.b64encode(master_salt).decode("ascii"),
                "tenant_salt_b64": base64.b64encode(tenant_salt).decode("ascii"),
                "master_key_fingerprint": key_fingerprint(master_key),
            },
            "envelope": encrypted_envelope,
        }
        self.encrypted_file.write_text(json.dumps(vault_payload, indent=2), encoding="utf-8")

        manifest_body = {
            "manifest_version": "1.0.0",
            "sealed_at_utc": vault_payload["created_at_utc"],
            "sealed_by": actor,
            "crypto_backend": backend_name(),
            "record_count": len(serialized_records),
            "merkle_root_sha256": merkle_root,
            "vault_ciphertext_sha256": sha256_hex(self.encrypted_file.read_bytes()),
            "master_key_fingerprint": key_fingerprint(master_key),
            "record_hashes": record_hashes,
        }
        manifest_sig = hmac_sha256_hex(
            master_key,
            json.dumps(manifest_body, sort_keys=True).encode("utf-8"),
        )
        manifest = {**manifest_body, "hmac_sha256_signature": manifest_sig}
        self.manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Write non-secret key & governance policy
        policy = {
            "policy_version": "1.0.0",
            "encryption_at_rest": "AES-256-GCM (NIST SP 800-38D)",
            "key_derivation": f"PBKDF2-HMAC-SHA256 ({PBKDF2_ITERATIONS:,} iterations)",
            "per_investor_isolation": "HKDF-SHA256 unique 256-bit tenant subkey + strict directory namespace guard",
            "integrity_protection": "Per-record SHA-256 + Merkle Root + HMAC-SHA256 signed manifest",
            "audit_logging": "Append-only SHA-256 hash-chained JSONL ledger",
            "pii_protection": "Automatic regex redaction of emails, IBANs, tax IDs (VKN/TCKN), and phone numbers before AI processing",
            "rbac_matrix": {r.value: sorted(perms) for r, perms in ROLE_PERMISSIONS.items()},
            "key_storage_rule": "Passphrase/master key MUST be injected via environment variable COP31_VAULT_PASSPHRASE or KMS; never committed to disk.",
        }
        self.policy_file.write_text(json.dumps(policy, indent=2), encoding="utf-8")

        self._append_audit(
            actor=actor,
            role=role.value,
            action="vault:seal",
            outcome="SUCCESS",
            details=f"Sealed {len(serialized_records)} verified COP31 investors; merkle_root={merkle_root[:16]}...",
        )
        return manifest

    def verify_integrity(
        self,
        passphrase: str,
        actor: str = "security_officer",
        role: SecurityRole = SecurityRole.SECURITY_OFFICER,
    ) -> dict:
        """Verify ciphertext hash, manifest HMAC signature, AES-GCM tag, and per-record Merkle root."""
        self._authorize(actor, role, "vault:verify")
        if not self.encrypted_file.exists() or not self.manifest_file.exists():
            raise VaultIntegrityError("Vault or integrity manifest missing. Run Step 1 seal first.")

        vault_payload = json.loads(self.encrypted_file.read_text(encoding="utf-8"))
        manifest = json.loads(self.manifest_file.read_text(encoding="utf-8"))

        # 1. Verify ciphertext file hash matches manifest
        actual_vault_hash = sha256_hex(self.encrypted_file.read_bytes())
        if not hmac.compare_digest(actual_vault_hash, manifest["vault_ciphertext_sha256"]):
            self._append_audit(actor, role.value, "vault:verify", "FAILED", "Encrypted vault file hash mismatch!")
            raise VaultIntegrityError("Tampering detected: encrypted vault ciphertext SHA-256 does not match manifest.")

        # 2. Re-derive master key & verify manifest HMAC signature
        kdf = vault_payload["kdf"]
        master_salt = base64.b64decode(kdf["master_salt_b64"])
        master_key = derive_master_key(passphrase, master_salt, iterations=int(kdf["iterations"]))

        recorded_sig = manifest["hmac_sha256_signature"]
        manifest_body = {k: v for k, v in manifest.items() if k != "hmac_sha256_signature"}
        expected_sig = hmac_sha256_hex(master_key, json.dumps(manifest_body, sort_keys=True).encode("utf-8"))
        if not hmac.compare_digest(recorded_sig, expected_sig):
            self._append_audit(actor, role.value, "vault:verify", "FAILED", "Manifest HMAC signature verification failed.")
            raise VaultIntegrityError("Manifest HMAC signature invalid (wrong passphrase or tampered manifest).")

        # 3. Decrypt AES-256-GCM payload & verify Merkle root over every single investor record
        plaintext = decrypt_aes256_gcm(master_key, vault_payload["envelope"], expected_aad=VAULT_AAD)
        data = json.loads(plaintext.decode("utf-8"))
        investors = [InvestorRecord.model_validate(item) for item in data["investors"]]

        recomputed_hashes = {inv.investor_id: canonical_record_hash(inv) for inv in investors}
        if recomputed_hashes != manifest["record_hashes"]:
            raise VaultIntegrityError("Per-record SHA-256 hashes do not match signed manifest.")

        recomputed_merkle = compute_merkle_root(list(recomputed_hashes.values()))
        if not hmac.compare_digest(recomputed_merkle, manifest["merkle_root_sha256"]):
            raise VaultIntegrityError("Merkle root mismatch across decrypted investor records.")

        self._append_audit(
            actor=actor,
            role=role.value,
            action="vault:verify",
            outcome="SUCCESS",
            details=f"Verified {len(investors)} records, AES-256-GCM tag, HMAC signature, and Merkle root {recomputed_merkle[:16]}...",
        )
        return {
            "verified": True,
            "record_count": len(investors),
            "merkle_root_sha256": recomputed_merkle,
            "crypto_backend": backend_name(),
            "master_key_fingerprint": key_fingerprint(master_key),
        }

    def load_verified_investors(
        self,
        passphrase: str,
        actor: str = "model_engineer",
        role: SecurityRole = SecurityRole.MODEL_ENGINEER,
    ) -> Tuple[List[InvestorRecord], bytes, bytes, Dict[str, str]]:
        """Verify vault integrity, decrypt investors, and return (investors, master_key, tenant_salt, record_hashes)."""
        self._authorize(actor, role, "vault:read")
        self.verify_integrity(passphrase=passphrase, actor=actor, role=role)

        vault_payload = json.loads(self.encrypted_file.read_text(encoding="utf-8"))
        manifest = json.loads(self.manifest_file.read_text(encoding="utf-8"))
        kdf = vault_payload["kdf"]
        master_salt = base64.b64decode(kdf["master_salt_b64"])
        tenant_salt = base64.b64decode(kdf["tenant_salt_b64"])
        master_key = derive_master_key(passphrase, master_salt, iterations=int(kdf["iterations"]))

        plaintext = decrypt_aes256_gcm(master_key, vault_payload["envelope"], expected_aad=VAULT_AAD)
        data = json.loads(plaintext.decode("utf-8"))
        investors = [InvestorRecord.model_validate(item) for item in data["investors"]]

        self._append_audit(
            actor=actor,
            role=role.value,
            action="vault:read",
            outcome="SUCCESS",
            details=f"Loaded {len(investors)} verified COP31 investors from encrypted vault.",
        )
        return investors, master_key, tenant_salt, manifest["record_hashes"]

    def log_model_or_form_event(
        self,
        actor: str,
        role: SecurityRole,
        action: str,
        outcome: str,
        details: str,
    ) -> None:
        """Public audit hook for Step 2 model builds and Step 3 form-filling executions."""
        self._append_audit(actor=actor, role=role.value, action=action, outcome=outcome, details=details)
