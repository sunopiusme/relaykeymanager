#!/usr/bin/env python3
"""
Telegram бот для выдачи бета-ключей Relay
С криптографической подписью Ed25519 и лимитом активаций

Установка:
  pip install -r requirements.txt

Настройка:
  1. Сгенерируй ключи: python crypto.py
  2. Установи переменные окружения:
     export TELEGRAM_BOT_TOKEN="your_token"
     export RELAY_BETA_SIGNING_KEY="private_key_hex"

Запуск:
  python telegram_beta_bot.py
"""

import json
import threading
import os
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, PreCheckoutQueryHandler, ContextTypes, filters


# === KEEP-ALIVE SERVER ===
class HealthHandler(BaseHTTPRequestHandler):
    """Simple health check endpoint to prevent sleep"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # Suppress logs


def start_health_server():
    """Start health check server in background thread"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"   Health server: http://0.0.0.0:{port}")

from config import (
    BOT_TOKEN, ADMIN_IDS, BETA_DAYS, BETA_COHORT,
    MAX_BETA_USERS, DATA_DIR, DATA_FILE, ED25519_PRIVATE_KEY_HEX,
    MAX_ACTIVATIONS_PER_KEY, TMA_URL, TMA_WEB_URL, DONATION_GOAL_STARS, STARS_PER_DOLLAR,
    DONATION_PRESETS_USD, DONATION_MILESTONES
)
from crypto import create_signed_beta_key, generate_discount_code, NACL_AVAILABLE
from activation_tracker import get_activation_stats

# Use Supabase for donations if available, fallback to JSON
USE_SUPABASE = True
try:
    from supabase_client import (
        record_donation, get_donation_stats, get_leaderboard,
        get_last_milestone, set_last_milestone
    )
    print("✅ Using Supabase for donations")
except ImportError as e:
    print(f"⚠️ Supabase not available ({e}), using JSON fallback")
    USE_SUPABASE = False
    from donations import (
        record_donation, get_donation_stats, get_leaderboard,
        get_last_milestone, set_last_milestone
    )

# Cached file_id for gif (set after first upload)
GIF_FILE_ID = None
GIF_PATH = Path(__file__).parent / "relaywebdemo.mp4"  # Use mp4, much smaller than gif

# === ЛОКАЛИЗАЦИЯ ===
TEXTS = {
    "en": {
        "welcome": "Hey! 👋\n\n"
                   "You know that feeling when you've got 30+ apps on your Mac, and half of them are probably outdated right now? "
                   "And you're kind of scared to update because... what if something breaks?\n\n"
                   "That's exactly why I built Relay.\n\n"
                   "It finds all your updates, lets you install them in one click, and here's the thing — "
                   "if an update messes something up, you can roll back in seconds. Not minutes. Seconds.\n\n"
                   "We're in beta right now, and I'm looking for people who actually care about keeping their Mac in shape.",
        "get_key_btn": "🔑 I'm in — get my key",
        "about_btn": "📖 Tell me more",
        "back_btn": "← Back",
        "about": "*The real problem nobody talks about*\n\n"
                 "You've got 30, 50, maybe 100 apps on your Mac. And here's what actually happens:\n\n"
                 "• Half of them are probably outdated right now\n"
                 "• Some update themselves, some don't, some just... sit there\n"
                 "• You skip updates because last time Figma broke after an update and you lost half a day\n"
                 "• Or you update everything and pray nothing explodes\n\n"
                 "Sound familiar?\n\n"
                 "*Here's what Relay actually does*\n\n"
                 "It scans your Mac, finds every app that has an update waiting, and shows you exactly what's new. "
                 "No guessing. No hunting through websites.\n\n"
                 "But here's the thing that changes everything:\n\n"
                 "Before Relay touches anything, it creates a backup. Automatically. In seconds. "
                 "Not a copy that eats up your disk — it uses APFS magic to make it instant and free.\n\n"
                 "So if an update breaks something? You hit one button and you're back. "
                 "Not tomorrow. Not after googling for an hour. Right now.\n\n"
                 "*What this means for you*\n\n"
                 "→ Update with confidence, not anxiety\n"
                 "→ Stop wasting time on manual checks\n"
                 "→ Never lose a workday to a bad update again\n"
                 "→ Keep your security tight without the hassle\n\n"
                 "*No Homebrew. No terminal. No account.*\n"
                 "Just a clean menu bar app that does one thing really well.\n\n"
                 f"As a beta tester, you get {BETA_DAYS} days of full access + 30% off at launch.\n\n"
                 "Ready? Tap /key",
        "no_slots": "Ah, you just missed it. All beta spots are taken.\n\n"
                    "But hey — drop your email or follow the channel, and I'll ping you the moment we open more slots or launch.",
        "already_have": "You're already in! Here's your key:\n\n"
                        "```\n{key}\n```\n\n"
                        "📅 Good until: {expires}\n"
                        "🎁 Your discount code: `{discount}` (30% off at launch)\n"
                        f"💻 Works on {MAX_ACTIVATIONS_PER_KEY} Macs\n\n"
                        "Just download Relay, go to Settings → License, paste the key. Done.\n\n"
                        "If anything's weird — just message me here.",
        "new_key": "*Welcome to the crew!* 🎉\n\n"
                   "You're beta tester #{num}. Here's your key:\n\n"
                   "```\n{key}\n```\n\n"
                   "📅 Valid until: {expires}\n"
                   "🎁 Your 30% discount: `{discount}`\n"
                   f"💻 Activate on up to {MAX_ACTIVATIONS_PER_KEY} Macs\n\n"
                   "*Quick setup:*\n"
                   "1. Download → https://relay-black.vercel.app/\n"
                   "2. Settings → License\n"
                   "3. Paste the key\n\n"
                   "That's it. You're in.\n\n"
                   "👽 Join our community to report bugs or share feedback:\n"
                   "https://t.me/+uNNdBeFK2wQzOWNi",
        "community_btn": "👽 Community & Bug Reports",
        "choose_lang": "🌍 Pick your language:",
        "crypto_error": "Something went wrong on my end. Give it a minute and try again?",
        "support_btn": "☕ Buy me a coffee",
        "support_text": "Building Relay is a one-person show. No VC money, no big team — just me, my Mac, and way too much coffee.\n\n"
                        "If Relay saves you time or headaches, you can fuel the next feature here. No pressure, no guilt — just good vibes.\n\n"
                        "Every coffee helps keep the lights on and the updates rolling. 🙏",
        "donate_stars_btn": "⭐ Donate with Stars",
        "donation_thanks": "🙏 *Thank you so much!*\n\n"
                           "You just donated *{amount} Stars*!\n\n"
                           "You're now #{rank} on the leaderboard 🏆\n\n"
                           "Your support means the world. Every star helps keep Relay alive and growing. 💫",
        "donation_thanks_simple": "🙏 *Thank you for your support!*\n\n"
                                   "Your donation helps keep Relay alive and growing. 💫",
        "donate_menu": "☕ *Support Relay Development*\n\n"
                       "Building Relay is a one-person show. No VC money, no big team — just me, my Mac, and way too much coffee.\n\n"
                       "📊 *Progress:* {progress_bar} {percent}%\n"
                       "⭐ {current} / {goal} Stars\n\n"
                       "Choose an amount to donate:",
        "donate_custom_prompt": "💫 *Custom Donation*\n\n"
                                "Enter the amount in USD (minimum $1):\n\n"
                                "Example: `5` for $5 or `10.50` for $10.50",
        "donate_custom_invalid": "❌ Invalid amount. Please enter a number between 1 and 1000.\n\n"
                                 "Example: `5` for $5",
        "donate_invoice_title": "Support Relay Development",
        "donate_invoice_desc": "Your donation helps keep Relay alive and growing. Thank you! 💫",
        "donate_btn_preset": "⭐ ${amount} ({stars} Stars)",
        "donate_btn_custom": "✏️ Custom Amount",
        "donate_btn_leaderboard": "🏆 View Leaderboard",
        "donate_btn_back": "← Back",
        "milestone_reached": "🎉 *Milestone Reached!*\n\n"
                             "Thanks to amazing supporters like you, Relay has reached *{milestone} Stars*!\n\n"
                             "This means so much. Your early support is literally making this project possible. 💫\n\n"
                             "Progress: {progress_bar} {percent}%",
        "goal_progress": "📊 *Donation Goal Progress*\n\n"
                         "{progress_bar} {percent}%\n"
                         "⭐ {current} / {goal} Stars (~${current_usd} / ${goal_usd})\n\n"
                         "👥 Total donors: {donors}\n\n"
                         "Every star counts! Use /donate to support.",
    },
    "ru": {
        "welcome": "Привет! 👋\n\n"
                   "Знакомо это чувство, когда на маке стоит куча приложений, и половина из них наверняка устарела? "
                   "А обновлять страшновато — вдруг что-то сломается и придётся разбираться?\n\n"
                   "Именно поэтому я сделал Relay.\n\n"
                   "Он находит все обновления, ставит их в один клик, и вот главное — "
                   "если апдейт что-то сломал, откат занимает секунды. Не минуты. Секунды.\n\n"
                   "Сейчас мы в бете, и я ищу людей, которым реально важно держать свой Mac в порядке.",
        "get_key_btn": "🔑 Я в деле — дай ключ",
        "about_btn": "📖 Расскажи подробнее",
        "back_btn": "← Назад",
        "about": "*Проблема, о которой никто не говорит*\n\n"
                 "У тебя на маке 30, 50, может 100 приложений. И вот что происходит на самом деле:\n\n"
                 "• Половина из них прямо сейчас устарела\n"
                 "• Какие-то обновляются сами, какие-то нет, какие-то просто... висят\n"
                 "• Ты пропускаешь апдейты, потому что в прошлый раз Figma сломалась после обновления и ты потерял полдня\n"
                 "• Или обновляешь всё разом и молишься, чтобы ничего не взорвалось\n\n"
                 "Знакомо?\n\n"
                 "*Что реально делает Relay*\n\n"
                 "Сканирует мак, находит каждое приложение с доступным обновлением, показывает что нового. "
                 "Без угадывания. Без охоты по сайтам.\n\n"
                 "Но вот что меняет всё:\n\n"
                 "Перед тем как Relay что-то тронет, он создаёт бэкап. Автоматически. За секунды. "
                 "Не копию, которая съест диск — он использует магию APFS, чтобы сделать это мгновенно и бесплатно.\n\n"
                 "Так что если апдейт что-то сломает? Жмёшь одну кнопку и ты обратно. "
                 "Не завтра. Не после часа гугления. Прямо сейчас.\n\n"
                 "*Что это значит для тебя*\n\n"
                 "→ Обновляй с уверенностью, а не с тревогой\n"
                 "→ Перестань тратить время на ручные проверки\n"
                 "→ Больше никогда не теряй рабочий день из-за плохого апдейта\n"
                 "→ Держи безопасность в порядке без головной боли\n\n"
                 "*Без Homebrew. Без терминала. Без аккаунта.*\n"
                 "Просто чистое menu bar приложение, которое делает одну вещь очень хорошо.\n\n"
                 f"Как бета-тестер получаешь {BETA_DAYS} дней полного доступа + скидку 30% на релизе.\n\n"
                 "Готов? Жми /key",
        "no_slots": "Эх, чуть-чуть не успел. Все бета-места разобрали.\n\n"
                    "Но слушай — подпишись на канал, и я напишу, как только откроем новые места или запустимся.",
        "already_have": "Ты уже в деле! Вот твой ключ:\n\n"
                        "```\n{key}\n```\n\n"
                        "📅 Работает до: {expires}\n"
                        "🎁 Твой код скидки: `{discount}` (30% на релизе)\n"
                        f"💻 Работает на {MAX_ACTIVATIONS_PER_KEY} маках\n\n"
                        "Скачай Relay, зайди в Settings → License, вставь ключ. Готово.\n\n"
                        "Если что-то не так — просто напиши мне сюда.",
        "new_key": "*Добро пожаловать в команду!* 🎉\n\n"
                   "Ты бета-тестер #{num}. Вот твой ключ:\n\n"
                   "```\n{key}\n```\n\n"
                   "📅 Действует до: {expires}\n"
                   "🎁 Твоя скидка 30%: `{discount}`\n"
                   f"💻 Активируй на {MAX_ACTIVATIONS_PER_KEY} маках\n\n"
                   "*Быстрый старт:*\n"
                   "1. Скачай → https://relay-black.vercel.app/\n"
                   "2. Settings → License\n"
                   "3. Вставь ключ\n\n"
                   "Всё. Ты в игре.\n\n"
                   "👽 Присоединяйся к комьюнити — баг-репорты и отзывы:\n"
                   "https://t.me/+uNNdBeFK2wQzOWNi",
        "community_btn": "👽 Комьюнити и баг-репорты",
        "choose_lang": "🌍 Выбери язык:",
        "crypto_error": "Что-то пошло не так на моей стороне. Подожди минутку и попробуй снова?",
        "support_btn": "☕ Угостить кофе",
        "support_text": "Relay — это проект одного человека. Без инвесторов, без большой команды — только я, мой мак и слишком много кофе.\n\n"
                        "Если Relay экономит тебе время или нервы, можешь поддержать разработку. Без давления, без обязательств — просто от души.\n\n"
                        "Каждая чашка помогает двигаться дальше. 🙏",
        "donate_stars_btn": "⭐ Донат через Stars",
        "donation_thanks": "🙏 *Огромное спасибо!*\n\n"
                           "Ты только что задонатил *{amount} Stars*!\n\n"
                           "Теперь ты #{rank} в лидерборде 🏆\n\n"
                           "Твоя поддержка бесценна. Каждая звезда помогает Relay жить и развиваться. 💫",
        "donation_thanks_simple": "🙏 *Спасибо за поддержку!*\n\n"
                                   "Твой донат помогает Relay жить и развиваться. 💫",
        "donate_menu": "☕ *Поддержать разработку Relay*\n\n"
                       "Relay — это проект одного человека. Без инвесторов, без большой команды — только я, мой мак и слишком много кофе.\n\n"
                       "📊 *Прогресс:* {progress_bar} {percent}%\n"
                       "⭐ {current} / {goal} Stars\n\n"
                       "Выбери сумму для доната:",
        "donate_custom_prompt": "💫 *Свой донат*\n\n"
                                "Введи сумму в долларах (минимум $1):\n\n"
                                "Пример: `5` для $5 или `10.50` для $10.50",
        "donate_custom_invalid": "❌ Неверная сумма. Введи число от 1 до 1000.\n\n"
                                 "Пример: `5` для $5",
        "donate_invoice_title": "Поддержка разработки Relay",
        "donate_invoice_desc": "Твой донат помогает Relay жить и развиваться. Спасибо! 💫",
        "donate_btn_preset": "⭐ ${amount} ({stars} Stars)",
        "donate_btn_custom": "✏️ Своя сумма",
        "donate_btn_leaderboard": "🏆 Лидерборд",
        "donate_btn_back": "← Назад",
        "milestone_reached": "🎉 *Достигнута веха!*\n\n"
                             "Благодаря таким замечательным людям как ты, Relay достиг *{milestone} Stars*!\n\n"
                             "Это очень много значит. Твоя ранняя поддержка буквально делает этот проект возможным. 💫\n\n"
                             "Прогресс: {progress_bar} {percent}%",
        "goal_progress": "📊 *Прогресс цели донатов*\n\n"
                         "{progress_bar} {percent}%\n"
                         "⭐ {current} / {goal} Stars (~${current_usd} / ${goal_usd})\n\n"
                         "👥 Всего донатеров: {donors}\n\n"
                         "Каждая звезда на счету! Используй /donate для поддержки.",
    }
}

# === ХРАНИЛИЩЕ ===
def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    ensure_data_dir()
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "keys_issued": 0, "user_langs": {}}

def save_data(data):
    ensure_data_dir()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_lang(user_id: int) -> str:
    data = load_data()
    return data.get("user_langs", {}).get(str(user_id), None)

def set_user_lang(user_id: int, lang: str):
    data = load_data()
    if "user_langs" not in data:
        data["user_langs"] = {}
    data["user_langs"][str(user_id)] = lang
    save_data(data)

def t(user_id: int, key: str) -> str:
    lang = get_user_lang(user_id) or "en"
    return TEXTS[lang].get(key, TEXTS["en"].get(key, key))

# === ГЕНЕРАЦИЯ КЛЮЧЕЙ ===
def generate_beta_key(user_id: int, username: str) -> str:
    """Generate cryptographically signed beta key"""
    if not NACL_AVAILABLE or not ED25519_PRIVATE_KEY_HEX:
        raise RuntimeError("Crypto not configured")
    
    return create_signed_beta_key(
        user_id=user_id,
        username=username,
        beta_days=BETA_DAYS,
        cohort=BETA_COHORT,
        private_key_hex=ED25519_PRIVATE_KEY_HEX
    )

# === КОМАНДЫ БОТА ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор языка при старте"""
    user_id = update.effective_user.id
    
    if get_user_lang(user_id):
        await show_main_menu(update, context)
        return
    
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 Choose your language / Выбери язык:",
        reply_markup=reply_markup
    )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка языка"""
    global GIF_FILE_ID
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = query.data.replace("lang_", "")
    set_user_lang(user_id, lang)
    
    keyboard = [
        [InlineKeyboardButton(t(user_id, "get_key_btn"), callback_data="get_key")],
        [InlineKeyboardButton(t(user_id, "about_btn"), callback_data="about")],
        [InlineKeyboardButton(t(user_id, "support_btn"), callback_data="support")],
        [InlineKeyboardButton(t(user_id, "community_btn"), url="https://t.me/+uNNdBeFK2wQzOWNi")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete language selection message
    await query.message.delete()
    
    # Send gif - use cached file_id or upload from disk
    if GIF_FILE_ID:
        msg = await context.bot.send_animation(
            chat_id=query.message.chat_id,
            animation=GIF_FILE_ID,
            caption=t(user_id, "welcome"),
            reply_markup=reply_markup
        )
    elif GIF_PATH.exists():
        with open(GIF_PATH, "rb") as gif_file:
            msg = await context.bot.send_animation(
                chat_id=query.message.chat_id,
                animation=gif_file,
                caption=t(user_id, "welcome"),
                reply_markup=reply_markup
            )
            # Cache file_id for future use
            if msg.animation:
                GIF_FILE_ID = msg.animation.file_id
    else:
        # Fallback to text if no gif
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t(user_id, "welcome"),
            reply_markup=reply_markup
        )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ главного меню"""
    global GIF_FILE_ID
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton(t(user_id, "get_key_btn"), callback_data="get_key")],
        [InlineKeyboardButton(t(user_id, "about_btn"), callback_data="about")],
        [InlineKeyboardButton(t(user_id, "support_btn"), callback_data="support")],
        [InlineKeyboardButton(t(user_id, "community_btn"), url="https://t.me/+uNNdBeFK2wQzOWNi")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send gif - use cached file_id or upload from disk
    if GIF_FILE_ID:
        await update.message.reply_animation(
            animation=GIF_FILE_ID,
            caption=t(user_id, "welcome"),
            reply_markup=reply_markup
        )
    elif GIF_PATH.exists():
        with open(GIF_PATH, "rb") as gif_file:
            msg = await update.message.reply_animation(
                animation=gif_file,
                caption=t(user_id, "welcome"),
                reply_markup=reply_markup
            )
            if msg.animation:
                GIF_FILE_ID = msg.animation.file_id
    else:
        await update.message.reply_text(
            t(user_id, "welcome"),
            reply_markup=reply_markup
        )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о Relay"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    keyboard = [
        [InlineKeyboardButton(t(user_id, "get_key_btn"), callback_data="get_key")],
        [InlineKeyboardButton(t(user_id, "back_btn"), callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Edit caption of the gif message
    try:
        await query.edit_message_caption(
            caption=t(user_id, "about"),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception:
        # Fallback: send new message if edit fails
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t(user_id, "about"),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к главному меню"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    keyboard = [
        [InlineKeyboardButton(t(user_id, "get_key_btn"), callback_data="get_key")],
        [InlineKeyboardButton(t(user_id, "about_btn"), callback_data="about")],
        [InlineKeyboardButton(t(user_id, "support_btn"), callback_data="support")],
        [InlineKeyboardButton(t(user_id, "community_btn"), url="https://t.me/+uNNdBeFK2wQzOWNi")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Edit caption of the gif message
    try:
        await query.edit_message_caption(
            caption=t(user_id, "welcome"),
            reply_markup=reply_markup
        )
    except Exception:
        await query.edit_message_text(
            t(user_id, "welcome"),
            reply_markup=reply_markup
        )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Страница поддержки проекта - теперь перенаправляет на /donate"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    await show_donate_menu(query.message.chat_id, user_id, context)


def make_progress_bar(current: int, goal: int, length: int = 10) -> str:
    """Create a text progress bar"""
    percent = min(current / goal, 1.0) if goal > 0 else 0
    filled = int(length * percent)
    empty = length - filled
    return "█" * filled + "░" * empty


async def show_donate_menu(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Show donation menu with preset amounts"""
    stats = get_donation_stats()
    current = stats["total_stars"]
    goal = DONATION_GOAL_STARS
    percent = int(min(current / goal * 100, 100)) if goal > 0 else 0
    progress_bar = make_progress_bar(current, goal)
    
    # Build keyboard with preset amounts
    keyboard = []
    for usd in DONATION_PRESETS_USD:
        stars = int(usd * STARS_PER_DOLLAR)
        btn_text = t(user_id, "donate_btn_preset").format(amount=usd, stars=stars)
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"donate_{usd}")])
    
    # Add custom amount and leaderboard buttons
    keyboard.append([InlineKeyboardButton(t(user_id, "donate_btn_custom"), callback_data="donate_custom")])
    keyboard.append([InlineKeyboardButton(t(user_id, "donate_btn_leaderboard"), web_app=WebAppInfo(url=f"{TMA_WEB_URL}/leaderboard"))])
    keyboard.append([InlineKeyboardButton(t(user_id, "donate_btn_back"), callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = t(user_id, "donate_menu").format(
        progress_bar=progress_bar,
        percent=percent,
        current=current,
        goal=goal
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /donate - show donation menu"""
    user_id = update.effective_user.id
    
    if not get_user_lang(user_id):
        set_user_lang(user_id, "en")
    
    await show_donate_menu(update.message.chat_id, user_id, context)


async def donate_preset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle preset donation amount selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Extract amount from callback data (e.g., "donate_4.99")
    try:
        usd_amount = float(query.data.replace("donate_", ""))
    except ValueError:
        return
    
    stars_amount = int(usd_amount * STARS_PER_DOLLAR)
    
    # Create invoice link
    await create_and_send_invoice(query.message.chat_id, user_id, stars_amount, usd_amount, context)


async def donate_custom_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom donation amount request"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Set state to wait for custom amount
    context.user_data["awaiting_custom_donation"] = True
    
    keyboard = [[InlineKeyboardButton(t(user_id, "donate_btn_back"), callback_data="donate_cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=t(user_id, "donate_custom_prompt"),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def donate_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel custom donation input"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    context.user_data["awaiting_custom_donation"] = False
    
    await show_donate_menu(query.message.chat_id, user_id, context)


async def handle_custom_donation_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for custom donation amount"""
    if not context.user_data.get("awaiting_custom_donation"):
        return
    
    user_id = update.effective_user.id
    text = update.message.text.strip().replace("$", "").replace(",", ".")
    
    try:
        usd_amount = float(text)
        if usd_amount < 1 or usd_amount > 1000:
            raise ValueError("Amount out of range")
    except ValueError:
        await update.message.reply_text(
            t(user_id, "donate_custom_invalid"),
            parse_mode="Markdown"
        )
        return
    
    context.user_data["awaiting_custom_donation"] = False
    stars_amount = int(usd_amount * STARS_PER_DOLLAR)
    
    await create_and_send_invoice(update.message.chat_id, user_id, stars_amount, usd_amount, context)


async def create_and_send_invoice(chat_id: int, user_id: int, stars_amount: int, usd_amount: float, context: ContextTypes.DEFAULT_TYPE):
    """Create invoice link and send payment button with Pay in App option"""
    import json
    
    payload = json.dumps({
        "type": "donation",
        "user_id": user_id,
        "stars": stars_amount,
        "usd": usd_amount
    })
    
    try:
        # Create invoice link using Bot API
        invoice_link = await context.bot.create_invoice_link(
            title=t(user_id, "donate_invoice_title"),
            description=t(user_id, "donate_invoice_desc"),
            payload=payload,
            currency="XTR",  # Telegram Stars
            prices=[LabeledPrice(label="Donation", amount=stars_amount)],
            provider_token=""  # Empty for digital goods
        )
        
        # TMA Web URL with query params for "Pay in App"
        # WebAppInfo requires direct HTTPS URL, not t.me link
        tma_pay_url = f"{TMA_WEB_URL}?amount={usd_amount}&stars={stars_amount}"
        
        # Send buttons: Pay directly + Pay in App
        keyboard = [
            [InlineKeyboardButton(
                f"⭐ Pay {stars_amount} Stars (${usd_amount:.2f})",
                url=invoice_link
            )],
            [InlineKeyboardButton(
                "📱 Pay in App",
                web_app=WebAppInfo(url=tma_pay_url)
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"💫 *Ready to donate ${usd_amount:.2f}*\n\n"
                 f"Click the button below to complete your donation of *{stars_amount} Stars*.\n\n"
                 f"Thank you for supporting Relay! 🙏",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        print(f"❌ Error creating invoice: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Failed to create payment. Please try again later."
        )


async def goal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /goal - show donation goal progress"""
    user_id = update.effective_user.id
    
    if not get_user_lang(user_id):
        set_user_lang(user_id, "en")
    
    stats = get_donation_stats()
    current = stats["total_stars"]
    goal = DONATION_GOAL_STARS
    percent = int(min(current / goal * 100, 100)) if goal > 0 else 0
    progress_bar = make_progress_bar(current, goal, 15)
    
    current_usd = current / STARS_PER_DOLLAR
    goal_usd = goal / STARS_PER_DOLLAR
    
    text = t(user_id, "goal_progress").format(
        progress_bar=progress_bar,
        percent=percent,
        current=current,
        goal=goal,
        current_usd=int(current_usd),
        goal_usd=int(goal_usd),
        donors=stats["total_donors"]
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def check_and_notify_milestone(stars_amount: int, context: ContextTypes.DEFAULT_TYPE):
    """Check if a milestone was reached and notify all donors"""
    stats = get_donation_stats()
    current = stats["total_stars"]
    last_milestone = get_last_milestone()
    
    for milestone in DONATION_MILESTONES:
        if current >= milestone > last_milestone:
            # Milestone reached!
            set_last_milestone(milestone)
            
            percent = int(min(current / DONATION_GOAL_STARS * 100, 100))
            progress_bar = make_progress_bar(current, DONATION_GOAL_STARS)
            
            # Notify all donors
            leaderboard = get_leaderboard(limit=1000)
            for donor in leaderboard:
                try:
                    donor_id = donor["id"]
                    text = t(donor_id, "milestone_reached").format(
                        milestone=milestone,
                        progress_bar=progress_bar,
                        percent=percent
                    )
                    await context.bot.send_message(
                        chat_id=donor_id,
                        text=text,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Failed to notify donor {donor.get('id')}: {e}")
            
            break  # Only notify for one milestone at a time

async def get_key_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выдача ключа по кнопке"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = user.id
    data = load_data()
    
    if data["keys_issued"] >= MAX_BETA_USERS:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t(user_id, "no_slots")
        )
        return
    
    user_id_str = str(user_id)
    if user_id_str in data["users"]:
        existing = data["users"][user_id_str]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t(user_id, "already_have").format(
                key=existing['key'],
                expires=existing['expires'],
                discount=existing['discount']
            ),
            parse_mode="Markdown"
        )
        return
    
    # Generate signed key
    try:
        beta_key = generate_beta_key(user_id, user.username)
    except RuntimeError:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t(user_id, "crypto_error")
        )
        return
    
    discount_code = generate_discount_code(user_id)
    expires = (datetime.now() + timedelta(days=BETA_DAYS)).strftime("%d.%m.%Y")
    
    data["users"][user_id_str] = {
        "username": user.username,
        "first_name": user.first_name,
        "key": beta_key,
        "discount": discount_code,
        "expires": expires,
        "issued_at": datetime.now().isoformat()
    }
    data["keys_issued"] += 1
    save_data(data)
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=t(user_id, "new_key").format(
            num=data['keys_issued'],
            key=beta_key,
            expires=expires,
            discount=discount_code
        ),
        parse_mode="Markdown"
    )

async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /key"""
    user = update.effective_user
    user_id = user.id
    data = load_data()
    
    if not get_user_lang(user_id):
        set_user_lang(user_id, "en")
    
    if data["keys_issued"] >= MAX_BETA_USERS:
        await update.message.reply_text(t(user_id, "no_slots"))
        return
    
    user_id_str = str(user_id)
    if user_id_str in data["users"]:
        existing = data["users"][user_id_str]
        await update.message.reply_text(
            t(user_id, "already_have").format(
                key=existing['key'],
                expires=existing['expires'],
                discount=existing['discount']
            ),
            parse_mode="Markdown"
        )
        return
    
    try:
        beta_key = generate_beta_key(user_id, user.username)
    except RuntimeError:
        await update.message.reply_text(t(user_id, "crypto_error"))
        return
    
    discount_code = generate_discount_code(user_id)
    expires = (datetime.now() + timedelta(days=BETA_DAYS)).strftime("%d.%m.%Y")
    
    data["users"][user_id_str] = {
        "username": user.username,
        "first_name": user.first_name,
        "key": beta_key,
        "discount": discount_code,
        "expires": expires,
        "issued_at": datetime.now().isoformat()
    }
    data["keys_issued"] += 1
    save_data(data)
    
    await update.message.reply_text(
        t(user_id, "new_key").format(
            num=data['keys_issued'],
            key=beta_key,
            expires=expires,
            discount=discount_code
        ),
        parse_mode="Markdown"
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /lang для смены языка"""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 Choose your language / Выбери язык:",
        reply_markup=reply_markup
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика (только для админов)"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    data = load_data()
    activation_stats = get_activation_stats()
    
    await update.message.reply_text(
        f"📊 *Beta Test Stats*\n\n"
        f"Keys issued: {data['keys_issued']}/{MAX_BETA_USERS}\n"
        f"Slots left: {MAX_BETA_USERS - data['keys_issued']}\n\n"
        f"*Activations:*\n"
        f"Total activations: {activation_stats['total_activations']}\n"
        f"Keys at limit: {activation_stats['keys_at_limit']}",
        parse_mode="Markdown"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рассылка (только для админов)"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = " ".join(context.args)
    data = load_data()
    sent = 0
    
    for user_id in data["users"]:
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 *News from Relay*\n\n{message}",
                parse_mode="Markdown"
            )
            sent += 1
        except Exception:
            pass
    
    await update.message.reply_text(f"✅ Sent to {sent} users")


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных из TMA после донатов"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user_id = update.effective_user.id
        action = data.get("action")
        
        if action == "donation_complete":
            amount = data.get("amount", 0)
            rank = data.get("rank")
            
            if rank:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=t(user_id, "donation_thanks").format(amount=amount, rank=rank),
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=t(user_id, "donation_thanks_simple"),
                    parse_mode="Markdown"
                )
    except Exception as e:
        print(f"Error handling webapp data: {e}")


# === TELEGRAM STARS PAYMENT HANDLERS ===

async def handle_pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle pre-checkout query for Telegram Stars payments.
    This is called when user clicks "Pay" in the invoice.
    We MUST respond within 10 seconds.
    """
    query = update.pre_checkout_query
    
    try:
        # Parse the payload to verify it's a valid donation
        payload = json.loads(query.invoice_payload)
        
        if payload.get("type") != "donation":
            await query.answer(ok=False, error_message="Invalid payment type")
            return
        
        # All checks passed - approve the payment
        await query.answer(ok=True)
        print(f"✅ Pre-checkout approved for user {query.from_user.id}, amount: {query.total_amount} Stars")
        
    except Exception as e:
        print(f"❌ Pre-checkout error: {e}")
        await query.answer(ok=False, error_message="Payment verification failed. Please try again.")


async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle successful Telegram Stars payment.
    This is called after the payment is confirmed.
    """
    payment = update.message.successful_payment
    user = update.effective_user
    user_id = user.id
    
    try:
        # Parse payload
        payload = json.loads(payment.invoice_payload)
        stars_amount = payment.total_amount
        
        print(f"💫 Payment received: {stars_amount} Stars from user {user_id} (@{user.username})")
        
        # Record the donation
        result = record_donation(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            stars_amount=stars_amount,
            charge_id=payment.telegram_payment_charge_id,
            photo_url=None  # We don't have photo_url in this context
        )
        
        rank = result["rank"]
        
        # Send thank you message
        await update.message.reply_text(
            t(user_id, "donation_thanks").format(amount=stars_amount, rank=rank),
            parse_mode="Markdown"
        )
        
        # Log for admin
        print(f"   Donor rank: #{rank}, Total donors: {result['total_donors']}")
        
        # Check for milestone notifications
        await check_and_notify_milestone(stars_amount, context)
        
    except Exception as e:
        print(f"❌ Error processing payment: {e}")
        # Still thank the user even if recording fails
        await update.message.reply_text(
            t(user_id, "donation_thanks_simple"),
            parse_mode="Markdown"
        )


async def donation_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show donation statistics (admin only)"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    stats = get_donation_stats()
    leaderboard = get_leaderboard(limit=5)
    
    top_donors = "\n".join([
        f"  {d['rank']}. {d['name']} - ⭐{d['total_stars']}"
        for d in leaderboard
    ]) if leaderboard else "  No donations yet"
    
    await update.message.reply_text(
        f"💰 *Donation Stats*\n\n"
        f"Total Stars: ⭐{stats['total_stars']}\n"
        f"Total USD: ${stats['total_usd']:.2f}\n"
        f"Total Donors: {stats['total_donors']}\n"
        f"Transactions: {stats['total_transactions']}\n\n"
        f"*Top 5 Donors:*\n{top_donors}",
        parse_mode="Markdown"
    )

# === ЗАПУСК ===
def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Set TELEGRAM_BOT_TOKEN!")
        print("   export TELEGRAM_BOT_TOKEN='token_from_botfather'")
        return
    
    if not NACL_AVAILABLE:
        print("❌ PyNaCl not installed!")
        print("   pip install pynacl")
        return
    
    if not ED25519_PRIVATE_KEY_HEX:
        print("⚠️  Warning: RELAY_BETA_SIGNING_KEY not set")
        print("   Generate keys: python crypto.py")
        print("   Then: export RELAY_BETA_SIGNING_KEY='your_private_key'")
    
    import asyncio
    import httpx
    
    # Force delete webhook before starting polling
    async def reset_webhook():
        async with httpx.AsyncClient() as client:
            await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true")
            await asyncio.sleep(2)  # Wait for Telegram to release the session
    
    asyncio.get_event_loop().run_until_complete(reset_webhook())
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("key", key_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("donations", donation_stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("donate", donate_command))
    app.add_handler(CommandHandler("goal", goal_command))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(get_key_callback, pattern="^get_key$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    app.add_handler(CallbackQueryHandler(donate_preset_callback, pattern="^donate_[0-9.]+$"))
    app.add_handler(CallbackQueryHandler(donate_custom_callback, pattern="^donate_custom$"))
    app.add_handler(CallbackQueryHandler(donate_cancel_callback, pattern="^donate_cancel$"))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_donation_amount))
    
    # Payment handlers for Telegram Stars
    app.add_handler(PreCheckoutQueryHandler(handle_pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))
    
    # Start health server for keep-alive
    start_health_server()
    
    print("🤖 Bot started!")
    print(f"   Limit: {MAX_BETA_USERS} keys")
    print(f"   Duration: {BETA_DAYS} days")
    print(f"   Max activations per key: {MAX_ACTIVATIONS_PER_KEY}")
    print("   Languages: EN/RU")
    print("   Crypto:", "✅ Enabled" if ED25519_PRIVATE_KEY_HEX else "⚠️ Not configured")
    print("   Stars Payments: ✅ Enabled")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
