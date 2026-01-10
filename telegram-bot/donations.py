"""
Donations management for Relay Bot
Handles Telegram Stars payments and leaderboard
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import DATA_DIR

DONATIONS_FILE = DATA_DIR / "donations.json"


def ensure_donations_file():
    """Ensure donations file exists"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DONATIONS_FILE.exists():
        save_donations_data({
            "donors": {},
            "total_stars": 0,
            "total_usd": 0,
            "transactions": []
        })


def load_donations_data() -> dict:
    """Load donations data from file"""
    ensure_donations_file()
    try:
        with open(DONATIONS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "donors": {},
            "total_stars": 0,
            "total_usd": 0,
            "transactions": []
        }


def save_donations_data(data: dict):
    """Save donations data to file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DONATIONS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
    Record a successful donation
    Returns donor info with updated rank
    """
    data = load_donations_data()
    user_id_str = str(user_id)
    
    # Stars to USD conversion (approximate)
    usd_amount = stars_amount / 50  # 50 stars ≈ $1
    
    # Update or create donor record
    if user_id_str in data["donors"]:
        donor = data["donors"][user_id_str]
        donor["total_stars"] += stars_amount
        donor["total_usd"] += usd_amount
        donor["donation_count"] += 1
        donor["last_donation"] = datetime.now().isoformat()
        if photo_url:
            donor["photo_url"] = photo_url
    else:
        name = f"{first_name} {last_name}".strip() if last_name else first_name
        data["donors"][user_id_str] = {
            "id": user_id,
            "name": name,
            "username": username,
            "total_stars": stars_amount,
            "total_usd": usd_amount,
            "donation_count": 1,
            "first_donation": datetime.now().isoformat(),
            "last_donation": datetime.now().isoformat(),
            "photo_url": photo_url
        }
    
    # Update totals
    data["total_stars"] += stars_amount
    data["total_usd"] += usd_amount
    
    # Record transaction
    data["transactions"].append({
        "user_id": user_id,
        "stars": stars_amount,
        "usd": usd_amount,
        "charge_id": charge_id,
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last 1000 transactions
    if len(data["transactions"]) > 1000:
        data["transactions"] = data["transactions"][-1000:]
    
    save_donations_data(data)
    
    # Calculate rank
    rank = get_donor_rank(user_id)
    
    return {
        "donor": data["donors"][user_id_str],
        "rank": rank,
        "total_donors": len(data["donors"])
    }


def get_donor_rank(user_id: int) -> int:
    """Get donor's rank in leaderboard"""
    data = load_donations_data()
    
    # Sort donors by total stars
    sorted_donors = sorted(
        data["donors"].items(),
        key=lambda x: x[1]["total_stars"],
        reverse=True
    )
    
    # Find user's position
    for i, (uid, _) in enumerate(sorted_donors):
        if uid == str(user_id):
            return i + 1
    
    return len(sorted_donors) + 1


def get_leaderboard(limit: int = 100) -> list:
    """Get top donors for leaderboard"""
    data = load_donations_data()
    
    # Sort by total stars
    sorted_donors = sorted(
        data["donors"].values(),
        key=lambda x: x["total_stars"],
        reverse=True
    )[:limit]
    
    # Add rank
    return [
        {**donor, "rank": i + 1}
        for i, donor in enumerate(sorted_donors)
    ]


def get_donation_stats() -> dict:
    """Get overall donation statistics"""
    data = load_donations_data()
    return {
        "total_stars": data["total_stars"],
        "total_usd": data["total_usd"],
        "total_donors": len(data["donors"]),
        "total_transactions": len(data["transactions"])
    }


def get_donor_info(user_id: int) -> Optional[dict]:
    """Get specific donor's info"""
    data = load_donations_data()
    user_id_str = str(user_id)
    
    if user_id_str in data["donors"]:
        donor = data["donors"][user_id_str]
        donor["rank"] = get_donor_rank(user_id)
        return donor
    
    return None


def get_last_milestone() -> int:
    """Get the last reached milestone"""
    data = load_donations_data()
    return data.get("last_milestone", 0)


def set_last_milestone(milestone: int):
    """Set the last reached milestone"""
    data = load_donations_data()
    data["last_milestone"] = milestone
    save_donations_data(data)
