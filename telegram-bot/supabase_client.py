"""
Supabase client for Relay Bot
Handles database operations for donations and beta users
"""

import os
from datetime import datetime
from typing import Optional
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dlavobqpdoclrrpipoaj.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_KEY:
            raise ValueError("SUPABASE_SECRET_KEY environment variable is required")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# ============================================
# TMA: Donation Functions
# ============================================

def record_donation(
    user_id: int,
    username: Optional[str],
    first_name: str,
    last_name: Optional[str],
    stars_amount: int,
    charge_id: str,
    photo_url: Optional[str] = None
) -> dict:
    """
    Record a successful donation using Supabase RPC function
    Returns donor info with updated rank
    """
    supabase = get_supabase()
    
    result = supabase.rpc('record_donation', {
        'p_user_id': user_id,
        'p_username': username,
        'p_first_name': first_name,
        'p_last_name': last_name,
        'p_photo_url': photo_url,
        'p_stars_amount': stars_amount,
        'p_charge_id': charge_id,
    }).execute()
    
    if result.data:
        row = result.data[0]
        return {
            "donor": {
                "total_stars": row['total_stars'],
                "total_usd": float(row['total_usd']),
                "donation_count": row['donation_count'],
            },
            "rank": row['rank'],
        }
    
    raise Exception("Failed to record donation")


def get_leaderboard(limit: int = 100) -> list:
    """Get top donors for leaderboard"""
    supabase = get_supabase()
    
    result = supabase.rpc('get_leaderboard', {
        'p_limit': limit,
        'p_user_id': None
    }).execute()
    
    return [
        {
            "rank": row['rank'],
            "id": row['user_id'],
            "name": row['name'],
            "username": row['username'],
            "photo_url": row['photo_url'],
            "total_stars": row['total_stars'],
            "total_usd": float(row['total_usd']),
        }
        for row in (result.data or [])
    ]


def get_donation_stats() -> dict:
    """Get overall donation statistics"""
    supabase = get_supabase()
    
    result = supabase.table('tma_donation_stats').select('*').eq('id', 1).single().execute()
    
    # Get transaction count
    tx_result = supabase.table('tma_transactions').select('id', count='exact').execute()
    tx_count = tx_result.count or 0
    
    if result.data:
        return {
            "total_stars": result.data['total_stars'],
            "total_usd": float(result.data['total_usd']),
            "total_donors": result.data['total_donors'],
            "last_milestone": result.data['last_milestone'],
            "total_transactions": tx_count,
        }
    
    return {
        "total_stars": 0,
        "total_usd": 0,
        "total_donors": 0,
        "last_milestone": 0,
        "total_transactions": 0,
    }


def get_donor_info(user_id: int) -> Optional[dict]:
    """Get specific donor's info with rank"""
    supabase = get_supabase()
    
    # Get donor from leaderboard view
    result = supabase.from_('tma_leaderboard').select('*').eq('user_id', user_id).execute()
    
    if result.data:
        row = result.data[0]
        return {
            "id": row['user_id'],
            "name": f"{row['first_name']} {row['last_name'] or ''}".strip(),
            "username": row['username'],
            "photo_url": row['photo_url'],
            "total_stars": row['total_stars'],
            "total_usd": float(row['total_usd']),
            "donation_count": row['donation_count'],
            "rank": row['rank'],
        }
    
    return None


def get_donor_rank(user_id: int) -> int:
    """Get donor's rank in leaderboard"""
    donor = get_donor_info(user_id)
    if donor:
        return donor['rank']
    return 0


def set_last_milestone(milestone: int):
    """Set the last reached milestone"""
    supabase = get_supabase()
    supabase.table('tma_donation_stats').update({
        'last_milestone': milestone
    }).eq('id', 1).execute()


def get_last_milestone() -> int:
    """Get the last reached milestone"""
    stats = get_donation_stats()
    return stats.get('last_milestone', 0)


# ============================================
# BOT: Beta Users Functions
# ============================================

def upsert_telegram_user(
    user_id: int,
    username: Optional[str],
    first_name: str,
    last_name: Optional[str] = None,
    photo_url: Optional[str] = None,
    language_code: Optional[str] = None
) -> dict:
    """Create or update a Telegram user"""
    supabase = get_supabase()
    
    result = supabase.table('telegram_users').upsert({
        'id': user_id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'photo_url': photo_url,
        'language_code': language_code,
        'updated_at': datetime.now().isoformat(),
    }).execute()
    
    return result.data[0] if result.data else {}


def create_beta_user(
    user_id: int,
    beta_key: str,
    expires_at: datetime,
    cohort: str = "beta-jan-2026"
) -> dict:
    """Create a new beta user"""
    supabase = get_supabase()
    
    result = supabase.table('bot_beta_users').insert({
        'user_id': user_id,
        'beta_key': beta_key,
        'cohort': cohort,
        'expires_at': expires_at.isoformat(),
        'is_active': True,
    }).execute()
    
    return result.data[0] if result.data else {}


def get_beta_user(user_id: int) -> Optional[dict]:
    """Get beta user by Telegram user ID"""
    supabase = get_supabase()
    
    result = supabase.table('bot_beta_users').select('*').eq('user_id', user_id).execute()
    
    return result.data[0] if result.data else None


def get_beta_user_by_key(beta_key: str) -> Optional[dict]:
    """Get beta user by beta key"""
    supabase = get_supabase()
    
    result = supabase.table('bot_beta_users').select('*').eq('beta_key', beta_key).execute()
    
    return result.data[0] if result.data else None


def record_activation(
    user_id: int,
    beta_key: str,
    machine_id: str
) -> dict:
    """Record a machine activation"""
    supabase = get_supabase()
    
    result = supabase.table('bot_activations').upsert({
        'user_id': user_id,
        'beta_key': beta_key,
        'machine_id': machine_id,
        'activated_at': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat(),
        'is_active': True,
    }).execute()
    
    return result.data[0] if result.data else {}


def get_activations_for_key(beta_key: str) -> list:
    """Get all activations for a beta key"""
    supabase = get_supabase()
    
    result = supabase.table('bot_activations').select('*').eq('beta_key', beta_key).eq('is_active', True).execute()
    
    return result.data or []


def count_active_beta_users() -> int:
    """Count total active beta users"""
    supabase = get_supabase()
    
    result = supabase.table('bot_beta_users').select('user_id', count='exact').eq('is_active', True).execute()
    
    return result.count or 0


def deactivate_beta_user(user_id: int):
    """Deactivate a beta user"""
    supabase = get_supabase()
    
    supabase.table('bot_beta_users').update({
        'is_active': False
    }).eq('user_id', user_id).execute()


def update_activation_last_seen(beta_key: str, machine_id: str):
    """Update last seen timestamp for an activation"""
    supabase = get_supabase()
    
    supabase.table('bot_activations').update({
        'last_seen': datetime.now().isoformat()
    }).eq('beta_key', beta_key).eq('machine_id', machine_id).execute()
