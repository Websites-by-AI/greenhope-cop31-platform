"""Cryptographic engine providing real AES-256-GCM authenticated encryption and HKDF-SHA256 tenant subkey derivation.

Backend resolution order:
1. `cryptography.hazmat.primitives.ciphers.aead.AESGCM` (when `cryptography` is installed)
2. Native OpenSSL `libcrypto` EVP AES-256-GCM via `ctypes` (zero extra pip dependencies, NIST SP 800-38D compliant)
"""

from __future__ import annotations

import base64
import ctypes
import ctypes.util
import hashlib
import hmac
import os
import secrets
from typing import Tuple

PBKDF2_ITERATIONS = 600_000
AES_KEY_BYTES = 32   # 256-bit key
GCM_NONCE_BYTES = 12 # 96-bit standard GCM nonce
GCM_TAG_BYTES = 16   # 128-bit authentication tag

# OpenSSL EVP_CTRL_GCM constants
_EVP_CTRL_GCM_SET_IVLEN = 0x9
_EVP_CTRL_GCM_GET_TAG = 0x10
_EVP_CTRL_GCM_SET_TAG = 0x11

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _CryptoAESGCM
    _HAS_CRYPTOGRAPHY = True
except ImportError:
    _CryptoAESGCM = None
    _HAS_CRYPTOGRAPHY = False


class CryptoEngineError(Exception):
    """Raised when encryption, decryption, or authentication tag verification fails."""


def derive_master_key(passphrase: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """Derive a 256-bit master key from passphrase and salt using PBKDF2-HMAC-SHA256."""
    if not passphrase or len(passphrase) < 12:
        raise CryptoEngineError("Passphrase must be at least 12 characters long.")
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, iterations, dklen=AES_KEY_BYTES)


def hkdf_sha256(ikm: bytes, salt: bytes, info: bytes, length: int = AES_KEY_BYTES) -> bytes:
    """RFC 5869 HKDF-SHA256 key derivation for per-investor cryptographic tenant isolation."""
    if not salt:
        salt = b"\x00" * 32
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    okm = bytearray()
    previous = b""
    counter = 1
    while len(okm) < length:
        previous = hmac.new(prk, previous + info + bytes([counter]), hashlib.sha256).digest()
        okm.extend(previous)
        counter += 1
    return bytes(okm[:length])


def derive_tenant_subkey(master_key: bytes, investor_id: str, tenant_salt: bytes) -> bytes:
    """Derive an isolated 256-bit key dedicated strictly to a single investor's KAG/RAG tenant."""
    info = f"cop31-investor-tenant-v1:{investor_id}".encode("utf-8")
    return hkdf_sha256(master_key, tenant_salt, info, length=AES_KEY_BYTES)


def key_fingerprint(key: bytes) -> str:
    """Return a non-reversible truncated SHA-256 fingerprint for safe logging/manifests."""
    return hashlib.sha256(b"cop31-key-fp:" + key).hexdigest()[:16]


class _OpenSSLAESGCM:
    """Direct ctypes binding to OpenSSL libcrypto EVP AES-256-GCM."""

    def __init__(self) -> None:
        lib_path = ctypes.util.find_library("crypto")
        if not lib_path:
            raise CryptoEngineError("Neither Python `cryptography` nor system OpenSSL `libcrypto` is available.")
        self._lib = ctypes.CDLL(lib_path)

        # Configure function signatures
        self._lib.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
        self._lib.EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]
        self._lib.EVP_aes_256_gcm.restype = ctypes.c_void_p

        self._lib.EVP_EncryptInit_ex.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        ]
        self._lib.EVP_EncryptInit_ex.restype = ctypes.c_int

        self._lib.EVP_DecryptInit_ex.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        ]
        self._lib.EVP_DecryptInit_ex.restype = ctypes.c_int

        self._lib.EVP_CIPHER_CTX_ctrl.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p
        ]
        self._lib.EVP_CIPHER_CTX_ctrl.restype = ctypes.c_int

        self._lib.EVP_EncryptUpdate.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.c_void_p, ctypes.c_int
        ]
        self._lib.EVP_EncryptUpdate.restype = ctypes.c_int

        self._lib.EVP_EncryptFinal_ex.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)
        ]
        self._lib.EVP_EncryptFinal_ex.restype = ctypes.c_int

        self._lib.EVP_DecryptUpdate.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.c_void_p, ctypes.c_int
        ]
        self._lib.EVP_DecryptUpdate.restype = ctypes.c_int

        self._lib.EVP_DecryptFinal_ex.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)
        ]
        self._lib.EVP_DecryptFinal_ex.restype = ctypes.c_int

    def encrypt(self, key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> Tuple[bytes, bytes]:
        if len(key) != AES_KEY_BYTES:
            raise CryptoEngineError("AES-256-GCM requires a 32-byte key.")
        ctx = self._lib.EVP_CIPHER_CTX_new()
        if not ctx:
            raise CryptoEngineError("Failed to allocate OpenSSL EVP_CIPHER_CTX.")
        try:
            if self._lib.EVP_EncryptInit_ex(ctx, self._lib.EVP_aes_256_gcm(), None, None, None) != 1:
                raise CryptoEngineError("EVP_EncryptInit_ex cipher setup failed.")
            if self._lib.EVP_CIPHER_CTX_ctrl(ctx, _EVP_CTRL_GCM_SET_IVLEN, len(nonce), None) != 1:
                raise CryptoEngineError("Failed to set GCM IV length.")
            if self._lib.EVP_EncryptInit_ex(ctx, None, None, key, nonce) != 1:
                raise CryptoEngineError("EVP_EncryptInit_ex key/iv setup failed.")

            out_len = ctypes.c_int(0)
            if aad:
                if self._lib.EVP_EncryptUpdate(ctx, None, ctypes.byref(out_len), aad, len(aad)) != 1:
                    raise CryptoEngineError("Failed to supply AAD during encryption.")

            out_buf = ctypes.create_string_buffer(len(plaintext) + 16)
            if self._lib.EVP_EncryptUpdate(ctx, out_buf, ctypes.byref(out_len), plaintext, len(plaintext)) != 1:
                raise CryptoEngineError("EVP_EncryptUpdate failed.")
            total_len = out_len.value

            final_len = ctypes.c_int(0)
            final_buf = ctypes.create_string_buffer(16)
            if self._lib.EVP_EncryptFinal_ex(ctx, final_buf, ctypes.byref(final_len)) != 1:
                raise CryptoEngineError("EVP_EncryptFinal_ex failed.")

            ciphertext = out_buf.raw[:total_len] + final_buf.raw[:final_len.value]

            tag_buf = ctypes.create_string_buffer(GCM_TAG_BYTES)
            if self._lib.EVP_CIPHER_CTX_ctrl(ctx, _EVP_CTRL_GCM_GET_TAG, GCM_TAG_BYTES, tag_buf) != 1:
                raise CryptoEngineError("Failed to extract GCM authentication tag.")
            return ciphertext, tag_buf.raw
        finally:
            self._lib.EVP_CIPHER_CTX_free(ctx)

    def decrypt(self, key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes) -> bytes:
        if len(key) != AES_KEY_BYTES:
            raise CryptoEngineError("AES-256-GCM requires a 32-byte key.")
        if len(tag) != GCM_TAG_BYTES:
            raise CryptoEngineError("Invalid GCM authentication tag length.")
        ctx = self._lib.EVP_CIPHER_CTX_new()
        if not ctx:
            raise CryptoEngineError("Failed to allocate OpenSSL EVP_CIPHER_CTX.")
        try:
            if self._lib.EVP_DecryptInit_ex(ctx, self._lib.EVP_aes_256_gcm(), None, None, None) != 1:
                raise CryptoEngineError("EVP_DecryptInit_ex cipher setup failed.")
            if self._lib.EVP_CIPHER_CTX_ctrl(ctx, _EVP_CTRL_GCM_SET_IVLEN, len(nonce), None) != 1:
                raise CryptoEngineError("Failed to set GCM IV length.")
            if self._lib.EVP_DecryptInit_ex(ctx, None, None, key, nonce) != 1:
                raise CryptoEngineError("EVP_DecryptInit_ex key/iv setup failed.")

            out_len = ctypes.c_int(0)
            if aad:
                if self._lib.EVP_DecryptUpdate(ctx, None, ctypes.byref(out_len), aad, len(aad)) != 1:
                    raise CryptoEngineError("Failed to supply AAD during decryption.")

            out_buf = ctypes.create_string_buffer(len(ciphertext) + 16)
            if self._lib.EVP_DecryptUpdate(ctx, out_buf, ctypes.byref(out_len), ciphertext, len(ciphertext)) != 1:
                raise CryptoEngineError("EVP_DecryptUpdate failed.")
            total_len = out_len.value

            tag_buf = ctypes.create_string_buffer(tag, GCM_TAG_BYTES)
            if self._lib.EVP_CIPHER_CTX_ctrl(ctx, _EVP_CTRL_GCM_SET_TAG, GCM_TAG_BYTES, tag_buf) != 1:
                raise CryptoEngineError("Failed to set expected GCM tag.")

            final_len = ctypes.c_int(0)
            final_buf = ctypes.create_string_buffer(16)
            if self._lib.EVP_DecryptFinal_ex(ctx, final_buf, ctypes.byref(final_len)) != 1:
                raise CryptoEngineError("Authentication tag verification failed! Ciphertext, key, or AAD was tampered with.")

            return out_buf.raw[:total_len] + final_buf.raw[:final_len.value]
        finally:
            self._lib.EVP_CIPHER_CTX_free(ctx)


_OPENSSL_ENGINE = None if _HAS_CRYPTOGRAPHY else _OpenSSLAESGCM()


def backend_name() -> str:
    return "cryptography.AESGCM" if _HAS_CRYPTOGRAPHY else "openssl-libcrypto-EVP-AES-256-GCM"


def encrypt_aes256_gcm(key: bytes, plaintext: bytes, aad: bytes = b"") -> dict:
    """Encrypt bytes with AES-256-GCM and return a portable JSON-serializable envelope."""
    nonce = secrets.token_bytes(GCM_NONCE_BYTES)
    if _HAS_CRYPTOGRAPHY:
        combined = _CryptoAESGCM(key).encrypt(nonce, plaintext, aad)
        ciphertext, tag = combined[:-GCM_TAG_BYTES], combined[-GCM_TAG_BYTES:]
    else:
        assert _OPENSSL_ENGINE is not None
        ciphertext, tag = _OPENSSL_ENGINE.encrypt(key, nonce, plaintext, aad)
    return {
        "algorithm": "AES-256-GCM",
        "backend": backend_name(),
        "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "aad_b64": base64.b64encode(aad).decode("ascii"),
        "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
        "tag_b64": base64.b64encode(tag).decode("ascii"),
    }


def decrypt_aes256_gcm(key: bytes, envelope: dict, expected_aad: bytes | None = None) -> bytes:
    """Decrypt and authenticate an AES-256-GCM envelope."""
    if envelope.get("algorithm") != "AES-256-GCM":
        raise CryptoEngineError(f"Unsupported algorithm: {envelope.get('algorithm')}")
    nonce = base64.b64decode(envelope["nonce_b64"])
    aad = base64.b64decode(envelope["aad_b64"])
    ciphertext = base64.b64decode(envelope["ciphertext_b64"])
    tag = base64.b64decode(envelope["tag_b64"])

    if expected_aad is not None and not hmac.compare_digest(aad, expected_aad):
        raise CryptoEngineError("AAD mismatch: envelope context does not match expected target.")

    if _HAS_CRYPTOGRAPHY:
        try:
            return _CryptoAESGCM(key).decrypt(nonce, ciphertext + tag, aad)
        except Exception as exc:
            raise CryptoEngineError("AES-256-GCM authentication tag verification failed.") from exc
    assert _OPENSSL_ENGINE is not None
    return _OPENSSL_ENGINE.decrypt(key, nonce, ciphertext, tag, aad)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hmac_sha256_hex(key: bytes, data: bytes) -> str:
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def generate_salt(length: int = 16) -> bytes:
    return os.urandom(length)
