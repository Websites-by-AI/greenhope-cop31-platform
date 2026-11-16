"""Per-investor cryptographic tenant isolation and PII sanitization for KAG/RAG model execution.

Ensures:
1. Investor A's knowledge graph, RAG chunks, and form context can NEVER cross into Investor B's runtime.
2. Sensitive applicant PII (VKN/TCKN tax IDs, IBANs, emails, phone numbers) is redacted before AI retrieval/LLM calls
   and only re-hydrated inside controlled final form assembly when explicitly authorized.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Tuple

from .crypto_engine import derive_tenant_subkey, key_fingerprint


class TenantIsolationError(PermissionError):
    """Raised when a cross-tenant file, graph, or corpus access is attempted."""


class TenantIsolationGuard:
    """Enforces strict filesystem namespace and cryptographic subkey isolation per investor model."""

    def __init__(self, models_root: Path, investor_id: str, master_key: bytes, tenant_salt: bytes) -> None:
        if not re.match(r"^inv_[a-z0-9_]+$", investor_id):
            raise TenantIsolationError(f"Invalid tenant investor_id format: {investor_id!r}")
        self.investor_id = investor_id
        self.namespace = f"tenant::{investor_id}"
        self.models_root = models_root.resolve()
        self.tenant_dir = (self.models_root / investor_id).resolve()

        # Prevent path traversal outside models_root
        if self.models_root not in self.tenant_dir.parents:
            raise TenantIsolationError(f"Path traversal blocked for tenant {investor_id}")

        self._subkey = derive_tenant_subkey(master_key, investor_id, tenant_salt)
        self.subkey_fingerprint = key_fingerprint(self._subkey)

    def assert_path_within_tenant(self, target_path: Path) -> Path:
        """Verify that every artifact read/write stays strictly inside this investor's directory."""
        resolved = target_path.resolve()
        if resolved != self.tenant_dir and self.tenant_dir not in resolved.parents:
            raise TenantIsolationError(
                f"Cross-tenant access blocked! Tenant '{self.investor_id}' attempted to access '{resolved}'."
            )
        return resolved

    def assert_investor_match(self, payload_investor_id: str) -> None:
        """Verify that every loaded KG node, RAG chunk, or manifest belongs to this tenant."""
        if payload_investor_id != self.investor_id:
            raise TenantIsolationError(
                f"Cross-tenant data leakage prevented! Expected '{self.investor_id}', received '{payload_investor_id}'."
            )

    @property
    def tenant_subkey(self) -> bytes:
        return self._subkey


class PIIRedactor:
    """Detects and masks sensitive applicant PII before KAG/RAG indexing, logging, or external LLM calls."""

    _EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    _IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
    _PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{2,4}[\s-]?\d{0,4}")
    _TR_TAX_RE = re.compile(r"\b(?:VKN|TCKN|TAX-ID)[:\s#-]*(\d{10,11})\b", re.IGNORECASE)

    @classmethod
    def redact_text(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace PII with deterministic reversible tokens and return (sanitized_text, token_map)."""
        token_map: Dict[str, str] = {}
        counter = 0

        def _replace(kind: str, match: re.Match) -> str:
            nonlocal counter
            counter += 1
            token = f"[REDACTED_{kind}_{counter}]"
            token_map[token] = match.group(0)
            return token

        redacted = cls._EMAIL_RE.sub(lambda m: _replace("EMAIL", m), text)
        redacted = cls._IBAN_RE.sub(lambda m: _replace("IBAN", m), redacted)
        redacted = cls._TR_TAX_RE.sub(lambda m: _replace("TAX_ID", m), redacted)
        # Only mask long phone-like sequences with >= 10 digits to avoid masking years/amounts
        def _phone_sub(m: re.Match) -> str:
            digits = re.sub(r"\D", "", m.group(0))
            if len(digits) >= 10 and not m.group(0).strip().startswith(("202", "203")):
                return _replace("PHONE", m)
            return m.group(0)

        redacted = cls._PHONE_RE.sub(_phone_sub, redacted)
        return redacted, token_map

    @classmethod
    def mask_identifier(cls, value: str | None) -> str:
        """Return a safe last-4 masked identifier for logs/forms (e.g., TR33****9012)."""
        if not value:
            return "NOT_PROVIDED"
        clean = value.strip()
        if len(clean) <= 4:
            return "*" * len(clean)
        return f"{clean[:2]}{'*' * (len(clean) - 6)}{clean[-4:]}" if len(clean) > 6 else f"{'*' * (len(clean) - 2)}{clean[-2:]}"
