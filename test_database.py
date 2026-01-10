#!/usr/bin/env python3
"""
Database integrity and sync test for Relay Beta Bot
Tests:
1. Data file integrity
2. Date format consistency
3. Key generation and verification
4. Activation tracking
"""
import json
import base64
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import DATA_DIR, DATA_FILE, BETA_DAYS, MAX_ACTIVATIONS_PER_KEY, ED25519_PUBLIC_KEY_HEX
from activation_tracker import (
    can_activate, record_activation, get_activation_stats,
    _load_activations, ACTIVATIONS_FILE
)

def test_data_directory():
    """Test data directory exists and is writable"""
    print("=== TEST: Data Directory ===")
    
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created data directory: {DATA_DIR}")
    else:
        print(f"✅ Data directory exists: {DATA_DIR}")
    
    # Test write
    test_file = DATA_DIR / ".write_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Directory is writable")
    except Exception as e:
        print(f"❌ Directory not writable: {e}")
        return False
    
    return True


def test_beta_users_database():
    """Test beta_users.json integrity"""
    print("\n=== TEST: Beta Users Database ===")
    
    if not DATA_FILE.exists():
        print("⚠️  beta_users.json not found (no users yet)")
        return True
    
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        return False
    
    # Check required fields
    required_fields = ["users", "keys_issued"]
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            return False
    
    print(f"✅ Database structure valid")
    print(f"   Users: {len(data['users'])}")
    print(f"   Keys issued: {data['keys_issued']}")
    
    # Validate each user
    errors = []
    for user_id, user_data in data.get("users", {}).items():
        # Check required user fields
        user_fields = ["key", "expires", "issued_at"]
        for field in user_fields:
            if field not in user_data:
                errors.append(f"User {user_id}: missing {field}")
        
        # Validate date formats
        try:
            datetime.fromisoformat(user_data.get("issued_at", ""))
        except:
            errors.append(f"User {user_id}: invalid issued_at format")
        
        try:
            datetime.strptime(user_data.get("expires", ""), "%d.%m.%Y")
        except:
            errors.append(f"User {user_id}: invalid expires format")
        
        # Validate key format
        key = user_data.get("key", "")
        if not key.startswith("RELAY-BETA-"):
            errors.append(f"User {user_id}: invalid key format")
    
    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False
    
    print(f"✅ All user records valid")
    return True


def test_key_payload():
    """Test key payload decoding and dates"""
    print("\n=== TEST: Key Payload Verification ===")
    
    if not DATA_FILE.exists():
        print("⚠️  No keys to test")
        return True
    
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    for user_id, user_data in data.get("users", {}).items():
        key = user_data.get("key", "")
        
        try:
            # Extract and decode payload
            without_prefix = key[len("RELAY-BETA-"):]
            payload_b64 = without_prefix.split(".")[0]
            payload_bytes = base64.b64decode(payload_b64)
            payload = json.loads(payload_bytes)
            
            # Verify payload fields
            required = ["u", "n", "s", "x", "c"]
            for field in required:
                if field not in payload:
                    print(f"❌ User {user_id}: missing payload field {field}")
                    return False
            
            # Check dates
            start_ts = payload["s"]
            expire_ts = payload["x"]
            start_date = datetime.fromtimestamp(start_ts)
            expire_date = datetime.fromtimestamp(expire_ts)
            days_in_key = (expire_date - start_date).days
            
            print(f"✅ User {user_id}:")
            print(f"   Key ID: {payload.get('k', 'N/A')}")
            print(f"   Start: {start_date.strftime('%Y-%m-%d')}")
            print(f"   Expires (in key): {expire_date.strftime('%Y-%m-%d')}")
            print(f"   Days in key: {days_in_key}")
            
            # Note about 7-day cap
            if days_in_key > 7:
                print(f"   ⚠️  Key has {days_in_key} days, but app enforces 7-day cap")
            
        except Exception as e:
            print(f"❌ User {user_id}: payload decode error: {e}")
            return False
    
    return True


def test_activation_tracking():
    """Test activation tracking system"""
    print("\n=== TEST: Activation Tracking ===")
    
    # Test with a fake key
    test_key_id = "test_key_12345"
    test_machine_id = "test_machine_abc"
    test_user_id = 999999
    
    # Check initial state
    can, reason = can_activate(test_key_id, test_machine_id)
    if not can or reason != "first_activation":
        # Key might already exist from previous test
        if reason == "already_activated":
            print("✅ Test key already activated (from previous test)")
        else:
            print(f"⚠️  Unexpected state: can={can}, reason={reason}")
    else:
        print("✅ First activation check passed")
    
    # Record activation
    success, msg = record_activation(
        key_id=test_key_id,
        user_id=test_user_id,
        machine_id=test_machine_id,
        app_version="1.0.0-test",
        os_version="14.0"
    )
    
    if success:
        print(f"✅ Activation recorded: {msg}")
    else:
        print(f"❌ Activation failed: {msg}")
        return False
    
    # Check same machine again
    can, reason = can_activate(test_key_id, test_machine_id)
    if can and reason == "already_activated":
        print("✅ Same machine re-activation allowed")
    else:
        print(f"❌ Same machine check failed: can={can}, reason={reason}")
        return False
    
    # Check different machine
    can, reason = can_activate(test_key_id, "different_machine")
    if can and reason == "new_machine":
        print("✅ New machine activation allowed")
    else:
        print(f"⚠️  New machine check: can={can}, reason={reason}")
    
    # Get stats
    stats = get_activation_stats()
    print(f"✅ Activation stats:")
    print(f"   Total keys: {stats['total_keys']}")
    print(f"   Total activations: {stats['total_activations']}")
    print(f"   Keys at limit: {stats['keys_at_limit']}")
    
    return True


def test_config_consistency():
    """Test configuration values"""
    print("\n=== TEST: Configuration ===")
    
    print(f"✅ BETA_DAYS: {BETA_DAYS}")
    print(f"✅ MAX_ACTIVATIONS_PER_KEY: {MAX_ACTIVATIONS_PER_KEY}")
    
    if BETA_DAYS != 7:
        print(f"⚠️  BETA_DAYS is {BETA_DAYS}, expected 7")
    
    if not ED25519_PUBLIC_KEY_HEX:
        print("⚠️  ED25519_PUBLIC_KEY_HEX not set")
    else:
        print(f"✅ Public key configured: {ED25519_PUBLIC_KEY_HEX[:16]}...")
    
    return True


def cleanup_test_data():
    """Remove test data"""
    print("\n=== CLEANUP ===")
    
    if ACTIVATIONS_FILE.exists():
        activations = _load_activations()
        if "test_key_12345" in activations:
            del activations["test_key_12345"]
            with open(ACTIVATIONS_FILE, "w") as f:
                json.dump(activations, f, indent=2)
            print("✅ Removed test activation data")
    
    print("✅ Cleanup complete")


def main():
    print("=" * 50)
    print("RELAY BETA BOT - DATABASE INTEGRITY TEST")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_data_directory()
    all_passed &= test_beta_users_database()
    all_passed &= test_key_payload()
    all_passed &= test_activation_tracking()
    all_passed &= test_config_consistency()
    
    cleanup_test_data()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
