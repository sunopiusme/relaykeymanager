"""
Configuration for Relay Beta Bot
"""
import os
from pathlib import Path

# Bot settings
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [123456789]  # Your Telegram ID

# Beta settings
BETA_DAYS = 7
BETA_COHORT = "beta-jan-2026"
MAX_BETA_USERS = 100
MAX_ACTIVATIONS_PER_KEY = 2  # Each key can be activated on 2 machines

# Paths
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "beta_users.json"

# Ed25519 private key for signing (generate with: openssl genpkey -algorithm ed25519)
# Store in environment variable for security
ED25519_PRIVATE_KEY_HEX = os.environ.get("RELAY_BETA_SIGNING_KEY", "")

# Public key (embed in app for verification)
# This is derived from private key and should be hardcoded in the Swift app
ED25519_PUBLIC_KEY_HEX = os.environ.get("RELAY_BETA_PUBLIC_KEY", "")

# Telegram Mini App URL for donations (leaderboard only)
TMA_URL = os.environ.get("RELAY_TMA_URL", "https://t.me/relaykeygen_bot/relaypayments")

# Donation settings
DONATION_GOAL_STARS = 50000  # Goal: 50,000 Stars (~$1000)
STARS_PER_DOLLAR = 50  # 50 Stars ≈ $1

# Preset donation amounts in USD
DONATION_PRESETS_USD = [4.99, 9.99, 19.99, 49.99]

# Milestone thresholds (in Stars) for notifications
DONATION_MILESTONES = [5000, 10000, 25000, 50000]  # ~$100, $200, $500, $1000
