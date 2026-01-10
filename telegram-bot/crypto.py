"""
Cryptographic utilities for beta key generation and verification
Uses Ed25519 signatures for tamper-proof keys
"""
import json
import base64
import hashlib
import time
from typing import Optional, Tuple
from dataclasses import dataclass

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import HexEncoder
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False
    print("⚠️  PyNaCl not installed. Run: pip install pynacl")


@dataclass
class BetaKeyPayload:
    """Payload embedded in beta key"""
    user_id: int          # Telegram user ID (unique identifier)
    username: str         # Telegram username
    start_ts: int         # Start timestamp
    expire_ts: int        # Expiration timestamp
    cohort: str           # Beta cohort identifier
    discount_code: str    # Discount code for this user
    key_id: str           # Unique key identifier for tracking activations


def generate_key_id(user_id: int) -> str:
    """Generate unique key ID from user_id and timestamp"""
    data = f"{user_id}-{int(time.time())}-relay"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def generate_discount_code(user_id: int) -> str:
    """Generate deterministic discount code for user"""
    hash_input = f"relay-beta-{user_id}".encode()
    digest = hashlib.sha256(hash_input).hexdigest()[:8].upper()
    return f"BETA{digest}"


def generate_keypair() -> Tuple[str, str]:
    """
    Generate new Ed25519 keypair for signing beta keys.
    Returns (private_key_hex, public_key_hex)
    
    Run this ONCE and store:
    - Private key: in RELAY_BETA_SIGNING_KEY env var (keep secret!)
    - Public key: hardcode in Swift app for verification
    """
    if not NACL_AVAILABLE:
        raise RuntimeError("PyNaCl required: pip install pynacl")
    
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    
    private_hex = signing_key.encode(encoder=HexEncoder).decode()
    public_hex = verify_key.encode(encoder=HexEncoder).decode()
    
    return private_hex, public_hex


def create_signed_beta_key(
    user_id: int,
    username: str,
    beta_days: int,
    cohort: str,
    private_key_hex: str
) -> str:
    """
    Create a cryptographically signed beta key.
    
    Format: RELAY-BETA-{base64_payload}.{base64_signature}
    
    The signature covers the entire payload, making it impossible to:
    - Forge keys without the private key
    - Modify expiration dates
    - Change user binding
    """
    if not NACL_AVAILABLE:
        raise RuntimeError("PyNaCl required: pip install pynacl")
    
    if not private_key_hex:
        raise ValueError("Private key not configured")
    
    now = int(time.time())
    expiration = now + (beta_days * 24 * 60 * 60)
    
    payload = BetaKeyPayload(
        user_id=user_id,
        username=username or "anonymous",
        start_ts=now,
        expire_ts=expiration,
        cohort=cohort,
        discount_code=generate_discount_code(user_id),
        key_id=generate_key_id(user_id)
    )
    
    # Compact JSON payload
    payload_dict = {
        "u": payload.user_id,
        "n": payload.username,
        "s": payload.start_ts,
        "x": payload.expire_ts,
        "c": payload.cohort,
        "d": payload.discount_code,
        "k": payload.key_id  # Key ID for activation tracking
    }
    
    payload_json = json.dumps(payload_dict, separators=(',', ':'))
    payload_bytes = payload_json.encode('utf-8')
    payload_b64 = base64.b64encode(payload_bytes).decode('ascii')
    
    # Sign the payload
    signing_key = SigningKey(private_key_hex, encoder=HexEncoder)
    signed = signing_key.sign(payload_bytes)
    signature_b64 = base64.b64encode(signed.signature).decode('ascii')
    
    return f"RELAY-BETA-{payload_b64}.{signature_b64}"


def verify_beta_key(key: str, public_key_hex: str) -> Optional[BetaKeyPayload]:
    """
    Verify a beta key signature and decode payload.
    Returns None if invalid.
    """
    if not NACL_AVAILABLE:
        return None
    
    if not key.startswith("RELAY-BETA-"):
        return None
    
    try:
        without_prefix = key[len("RELAY-BETA-"):]
        parts = without_prefix.split(".")
        
        if len(parts) != 2:
            return None
        
        payload_b64, signature_b64 = parts
        payload_bytes = base64.b64decode(payload_b64)
        signature_bytes = base64.b64decode(signature_b64)
        
        # Verify signature
        verify_key = VerifyKey(public_key_hex, encoder=HexEncoder)
        verify_key.verify(payload_bytes, signature_bytes)
        
        # Decode payload
        payload_dict = json.loads(payload_bytes.decode('utf-8'))
        
        return BetaKeyPayload(
            user_id=payload_dict["u"],
            username=payload_dict["n"],
            start_ts=payload_dict["s"],
            expire_ts=payload_dict["x"],
            cohort=payload_dict["c"],
            discount_code=payload_dict["d"],
            key_id=payload_dict.get("k", "")
        )
        
    except Exception:
        return None


if __name__ == "__main__":
    # Generate new keypair
    print("🔐 Generating Ed25519 keypair for beta key signing...\n")
    
    private_key, public_key = generate_keypair()
    
    print("Private key (KEEP SECRET - store in RELAY_BETA_SIGNING_KEY):")
    print(f"  {private_key}\n")
    
    print("Public key (embed in Swift app for verification):")
    print(f"  {public_key}\n")
    
    print("Swift code for app:")
    print(f'  static let betaPublicKey = "{public_key}"')
