"""Security package for Step 1: Verification, Encryption at Rest, RBAC, PII Redaction, Audit Chaining, and Tenant Isolation."""

from .crypto_engine import (
    CryptoEngineError,
    backend_name,
    decrypt_aes256_gcm,
    derive_master_key,
    derive_tenant_subkey,
    encrypt_aes256_gcm,
    hmac_sha256_hex,
    key_fingerprint,
    sha256_hex,
)
from .tenant_guard import PIIRedactor, TenantIsolationError, TenantIsolationGuard
from .vault import AccessDeniedError, InvestorSecurityVault, VaultIntegrityError

__all__ = [
    "AccessDeniedError",
    "CryptoEngineError",
    "InvestorSecurityVault",
    "PIIRedactor",
    "TenantIsolationError",
    "TenantIsolationGuard",
    "VaultIntegrityError",
    "backend_name",
    "decrypt_aes256_gcm",
    "derive_master_key",
    "derive_tenant_subkey",
    "encrypt_aes256_gcm",
    "hmac_sha256_hex",
    "key_fingerprint",
    "sha256_hex",
]
