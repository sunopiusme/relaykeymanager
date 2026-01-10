"""
Migration script: JSON files → Supabase
Migrates existing data from local JSON files to Supabase database
"""

import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from supabase import create_client

# Configuration
DATA_DIR = Path(__file__).parent / "data"
DONATIONS_FILE = DATA_DIR / "donations.json"
BETA_USERS_FILE = DATA_DIR / "beta_users.json"
ACTIVATIONS_FILE = DATA_DIR / "activations.json"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY")


def get_supabase():
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY are required")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def migrate_donations():
    """Migrate donations data from JSON to Supabase"""
    if not DONATIONS_FILE.exists():
        print("No donations.json found, skipping donations migration")
        return
    
    print("Migrating donations...")
    
    with open(DONATIONS_FILE, "r") as f:
        data = json.load(f)
    
    supabase = get_supabase()
    
    # Migrate donors
    donors = data.get("donors", {})
    print(f"Found {len(donors)} donors to migrate")
    
    for user_id_str, donor in donors.items():
        user_id = int(user_id_str)
        
        # First, create/update telegram user
        name_parts = donor.get("name", "Unknown").split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else None
        
        try:
            supabase.table('telegram_users').upsert({
                'id': user_id,
                'username': donor.get('username'),
                'first_name': first_name,
                'last_name': last_name,
                'photo_url': donor.get('photo_url'),
            }).execute()
            
            # Then create donor record
            supabase.table('tma_donors').upsert({
                'user_id': user_id,
                'total_stars': donor.get('total_stars', 0),
                'total_usd': donor.get('total_usd', 0),
                'donation_count': donor.get('donation_count', 0),
                'first_donation': donor.get('first_donation', datetime.now().isoformat()),
                'last_donation': donor.get('last_donation', datetime.now().isoformat()),
            }).execute()
            
            print(f"  ✓ Migrated donor {user_id} ({donor.get('name')})")
        except Exception as e:
            print(f"  ✗ Failed to migrate donor {user_id}: {e}")
    
    # Migrate transactions
    transactions = data.get("transactions", [])
    print(f"Found {len(transactions)} transactions to migrate")
    
    for tx in transactions:
        try:
            supabase.table('tma_transactions').insert({
                'user_id': tx['user_id'],
                'stars_amount': tx['stars'],
                'usd_amount': tx['usd'],
                'charge_id': tx['charge_id'],
                'status': 'completed',
                'created_at': tx.get('timestamp', datetime.now().isoformat()),
            }).execute()
            print(f"  ✓ Migrated transaction {tx['charge_id']}")
        except Exception as e:
            # Skip duplicates
            if '23505' in str(e):
                print(f"  - Skipped duplicate transaction {tx['charge_id']}")
            else:
                print(f"  ✗ Failed to migrate transaction: {e}")
    
    # Update global stats
    try:
        supabase.table('tma_donation_stats').upsert({
            'id': 1,
            'total_stars': data.get('total_stars', 0),
            'total_usd': data.get('total_usd', 0),
            'total_donors': len(donors),
            'last_milestone': data.get('last_milestone', 0),
        }).execute()
        print("  ✓ Updated global donation stats")
    except Exception as e:
        print(f"  ✗ Failed to update stats: {e}")
    
    print("Donations migration complete!")


def migrate_beta_users():
    """Migrate beta users data from JSON to Supabase"""
    if not BETA_USERS_FILE.exists():
        print("No beta_users.json found, skipping beta users migration")
        return
    
    print("Migrating beta users...")
    
    with open(BETA_USERS_FILE, "r") as f:
        data = json.load(f)
    
    supabase = get_supabase()
    
    users = data.get("users", {})
    print(f"Found {len(users)} beta users to migrate")
    
    for user_id_str, user in users.items():
        user_id = int(user_id_str)
        
        try:
            # Create telegram user first
            supabase.table('telegram_users').upsert({
                'id': user_id,
                'username': user.get('username'),
                'first_name': user.get('first_name', 'Unknown'),
                'last_name': user.get('last_name'),
            }).execute()
            
            # Create beta user record
            supabase.table('bot_beta_users').upsert({
                'user_id': user_id,
                'beta_key': user.get('beta_key', ''),
                'cohort': user.get('cohort', 'beta-jan-2026'),
                'activated_at': user.get('activated_at', datetime.now().isoformat()),
                'expires_at': user.get('expires_at', datetime.now().isoformat()),
                'is_active': user.get('is_active', True),
            }).execute()
            
            print(f"  ✓ Migrated beta user {user_id}")
        except Exception as e:
            print(f"  ✗ Failed to migrate beta user {user_id}: {e}")
    
    print("Beta users migration complete!")


def migrate_activations():
    """Migrate activations data from JSON to Supabase"""
    if not ACTIVATIONS_FILE.exists():
        print("No activations.json found, skipping activations migration")
        return
    
    print("Migrating activations...")
    
    with open(ACTIVATIONS_FILE, "r") as f:
        data = json.load(f)
    
    supabase = get_supabase()
    
    activations = data.get("activations", [])
    print(f"Found {len(activations)} activations to migrate")
    
    for activation in activations:
        try:
            supabase.table('bot_activations').upsert({
                'user_id': activation['user_id'],
                'beta_key': activation['beta_key'],
                'machine_id': activation['machine_id'],
                'activated_at': activation.get('activated_at', datetime.now().isoformat()),
                'last_seen': activation.get('last_seen'),
                'is_active': activation.get('is_active', True),
            }).execute()
            print(f"  ✓ Migrated activation for machine {activation['machine_id'][:8]}...")
        except Exception as e:
            print(f"  ✗ Failed to migrate activation: {e}")
    
    print("Activations migration complete!")


def main():
    """Run all migrations"""
    print("=" * 50)
    print("Starting migration to Supabase")
    print("=" * 50)
    print()
    
    try:
        migrate_donations()
        print()
        migrate_beta_users()
        print()
        migrate_activations()
        print()
        print("=" * 50)
        print("Migration complete!")
        print("=" * 50)
    except Exception as e:
        print(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    main()
