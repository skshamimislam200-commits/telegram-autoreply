import asyncio
import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# ⚙️ CONFIG
# ============================================================
API_ID = int(os.getenv("API_ID", "35398542"))
API_HASH = os.getenv("API_HASH", "e7991fac34e488dbc41f95125a778cfa")
SESSION_STRING = os.getenv("SESSION_STRING", "")
WELCOME_BOT_TOKEN = os.getenv("WELCOME_BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "7918793670"))

GROUP_REMINDER_INTERVAL = 60 * 60  # প্রতি ১ ঘণ্টায় reminder
OWNER_REPLY_TIMEOUT = 10 * 60      # 10 minutes

# Group active time: সকাল ৮:৩০ - রাত ৯:৩০
GROUP_OPEN_HOUR = 8
GROUP_OPEN_MINUTE = 30
GROUP_CLOSE_HOUR = 21
GROUP_CLOSE_MINUTE = 30

BOT_SIGNATURE = "[ DEVELOPER SHAMIM ]"

# ============================================================
# 🚫 BAD WORDS LIST (বাংলা + ইংরেজি + Romanized)
# ============================================================
BAD_WORDS = [
    # বাংলা গালি
    "মাদারচোদ", "মাদারচুদ", "বাল", "বালছাল", "চোদ", "চুদ", "চুদি",
    "শালা", "হারামি", "হারামজাদা", "কুত্তা", "কুত্তার বাচ্চা",
    "বেশ্যা", "রান্ডি", "খানকি", "মাগি", "ভোদা", "ভোদাই",
    "গাধা", "গু", "হিজড়া", "শুয়োর", "শুয়োরের বাচ্চা",
    "কামিনী", "ছিনাল", "বজ্জাত", "নোংরা", "বেহায়া", "ফাজিল",
    # ইংরেজি গালি
    "fuck", "fucker", "fucking", "fuk", "f*ck", "f**k",
    "shit", "bitch", "bastard", "asshole", "ass", "arse",
    "dick", "cock", "pussy", "whore", "slut",
    "cunt", "nigga", "nigger", "motherfucker", "mf",
    "idiot", "stupid", "moron", "dumb", "loser",
    "wtf", "stfu", "gtfo", "kys",
    # Romanized বাংলা
    "bal", "chod", "chud", "harami", "haramjada",
    "khankir", "magi", "hijra", "shuorer", "gadha",
    "sala", "shala", "madar", "madarjat", "beshsha",
]

# ============================================================
# 💬 USERBOT MESSAGES
# ============================================================
BUSY_MESSAGE = (
    "╔══════════════════════╗\n"
    "║   📬  MESSAGE RECEIVED   ║\n"
    "╚══════════════════════╝\n\n"
    "হ্যালো! 👋 আপনার message পৌঁছে গেছে ✅\n\n"
    "┌─────────────────────┐\n"
    "│  🔴  Owner এখন busy আছেন  │\n"
    "└─────────────────────┘\n\n"
    "⏳ সময়সীমা:\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🕐 ৩০ - ৬০ মিনিটের মধ্যে\n"
    "   আপনাকে reply করা হবে\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "💙 ধৈর্য ধরার জন্য আন্তরিক\n"
    "   ধন্যবাদ! 🙏\n\n"
    "[ DEVELOPER SHAMIM ]"
)

SLEEP_MESSAGE = (
    "╔══════════════════════╗\n"
    "║   🌙  GOOD NIGHT MODE    ║\n"
    "╚══════════════════════╝\n\n"
    "হ্যালো! 👋 আপনার message পৌঁছে গেছে ✅\n\n"
    "┌─────────────────────┐\n"
    "│  😴  Owner এখন ঘুমাচ্ছেন  │\n"
    "└─────────────────────┘\n\n"
    "🌛 রাতের বিশ্রাম চলছে...\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⏰ আগামীকাল সকাল ৮:৩০ এ\n"
    "   আপনাকে reply দেওয়া হবে\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "🌟 শুভ রাত্রি! ভালো থাকুন 🙏\n\n"
    "[ DEVELOPER SHAMIM ]"
)

WELCOME_MESSAGE = (
    "╔══════════════════════════╗\n"
    "║   🎉  WELCOME TO THE GROUP!   ║\n"
    "╚══════════════════════════╝\n\n"
    "হ্যালো {name}! 👋\n"
    "আমাদের গ্রুপে আপনাকে স্বাগতম! 🌟\n\n"
    "┌──────────────────────────┐\n"
    "│  📌 গ্রুপের নিয়মকানুন মেনে চলুন  │\n"
    "│  🤝 সবার সাথে ভালো ব্যবহার করুন  │\n"
    "│  💬 যেকোনো সমস্যায় admin দের     │\n"
    "│     সাথে যোগাযোগ করুন            │\n"
    "└──────────────────────────┘\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "আশা করি এখানে আপনার ভালো লাগবে! 😊\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "[ DEVELOPER SHAMIM ]"
)

REMINDER_MESSAGE = (
    "╔══════════════════════╗\n"
    "║   🔔  ADMIN REMINDER     ║\n"
    "╚══════════════════════╝\n\n"
    "হ্যালো সবাই! 👋\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "❓ কারো কোনো সমস্যা আছে?\n"
    "💬 থাকলে এখানে জানান\n"
    "🛠️ Admin সমাধান করে দেবেন!\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "[ DEVELOPER SHAMIM ]"
)

WAIT_SECONDS = 300
REPLY_COOLDOWN = 30 * 60  # ৩০ মিনিট

# ============================================================
# 🤖 USERBOT CLIENT
# ============================================================
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("shamim_userbot", API_ID, API_HASH)

owner_replied: set = set()
idle_timers: dict = {}
problem_tracking: dict = {}
pending_problems: dict = {}
group_chat_ids: set = set()
# last_replied: {user_id: timestamp} — শেষবার কখন reply দিয়েছি
last_replied: dict = {}


def get_auto_reply():
    now = datetime.now()
    # সকাল ৮:৩০ থেকে রাত ৯:৩০ → Busy
    # বাকি সময় → Sleep
    start = now.replace(hour=8, minute=30, second=0, microsecond=0)
    end = now.replace(hour=21, minute=30, second=0, microsecond=0)
    if start <= now < end:
        return BUSY_MESSAGE
    return SLEEP_MESSAGE


def contains_bad_word(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word.lower() in text_lower:
            return True
    return False


async def reactivate_bot(user_id):
    await asyncio.sleep(WAIT_SECONDS)
    owner_replied.discard(user_id)
    idle_timers.pop(user_id, None)
    print(f"🔔 Bot আবার চালু: [{user_id}]")


def reset_idle_timer(user_id):
    if user_id in idle_timers:
        idle_timers[user_id].cancel()
    task = asyncio.create_task(reactivate_bot(user_id))
    idle_timers[user_id] = task


# ============================================================
# 📨 PRIVATE MESSAGE HANDLERS
# ============================================================
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def incoming_handler(event):
    sender = await event.get_sender()
    sender_id = sender.id
    if sender.bot:
        return
    if sender_id in owner_replied:
        return

    # ১ ঘণ্টার মধ্যে আগে reply দিয়ে থাকলে আবার দেবে না
    now = datetime.now().timestamp()
    last = last_replied.get(sender_id, 0)
    if now - last < REPLY_COOLDOWN:
        print(f"⏸ Cooldown active: {sender.first_name} [ID: {sender_id}]")
        return

    reply_msg = get_auto_reply()
    now_dt = datetime.now()
    start = now_dt.replace(hour=8, minute=30, second=0, microsecond=0)
    end = now_dt.replace(hour=21, minute=30, second=0, microsecond=0)
    mode = "🌞 Day" if start <= now_dt < end else "🌙 Sleep"
    await event.reply(reply_msg)
    last_replied[sender_id] = now
    print(f"✅ Auto-replied [{mode}]: {sender.first_name} [ID: {sender_id}]")


@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def outgoing_handler(event):
    chat = await event.get_chat()
    receiver_id = chat.id
    owner_replied.add(receiver_id)
    reset_idle_timer(receiver_id)
    # আপনি reply করলে ওই user এর cooldown reset করো
    last_replied.pop(receiver_id, None)
    print(f"🔕 Bot বন্ধ + timer: [{receiver_id}]")


# ============================================================
# 🎉 WELCOME BOT
# ============================================================
def tg_api(token, method, data):
    url = f"https://api.telegram.org/bot{token}/{method}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"⚠️ API error [{method}]: {e}")
        return {}


def handle_group_message(token, msg, owner_id):
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    chat_type = chat.get("type", "")
    if chat_type not in ["group", "supergroup"]:
        return

    group_chat_ids.add(chat_id)

    msg_id = msg.get("message_id")
    sender = msg.get("from", {})
    sender_id = sender.get("id")
    sender_name = sender.get("first_name", "কেউ")
    sender_username = sender.get("username", "")
    sender_mention = f"@{sender_username}" if sender_username else sender_name
    text = msg.get("text", "") or msg.get("caption", "") or ""

    # Voice delete
    if msg.get("voice") or msg.get("video_note"):
        tg_api(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
        tg_api(token, "sendMessage", {
            "chat_id": chat_id,
            "text": (
                f"🚫 {sender_mention} এর voice message delete করা হয়েছে!\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"⚠️ এই group এ voice message নিষিদ্ধ।\n"
                f"💬 Text এ লিখুন।\n\n"
                f"{BOT_SIGNATURE}"
            )
        })
        print(f"🗑️ Voice deleted: {sender_name}")
        return

    # Bad word delete
    if contains_bad_word(text):
        tg_api(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
        tg_api(token, "sendMessage", {
            "chat_id": chat_id,
            "text": (
                f"⛔ {sender_mention} এর message delete করা হয়েছে!\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🚫 অশ্লীল শব্দ ব্যবহার নিষিদ্ধ।\n"
                f"✅ ভদ্রভাবে কথা বলুন।\n\n"
                f"{BOT_SIGNATURE}"
            )
        })
        print(f"🗑️ Bad word deleted: {sender_name}")
        return

    # Problem detection
    problem_keywords = [
        "সমস্যা", "problem", "plm", "help", "হেল্প",
        "সাহায্য", "pls", "please", "issue", "fix",
        "কাজ করছে না", "হচ্ছে না", "পারছি না", "বুঝছি না"
    ]
    has_problem = any(w in text.lower() for w in problem_keywords)

    if has_problem and sender_id:
        if sender_id not in problem_tracking:
            problem_tracking[sender_id] = {
                "chat_id": chat_id,
                "name": sender_mention,
                "waiting": True,
                "msg_id": msg_id,
                "time": datetime.now().timestamp()
            }
            tg_api(token, "sendMessage", {
                "chat_id": chat_id,
                "text": (
                    f"🤝 {sender_mention} আপনার সমস্যার কথা শুনলাম!\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"💬 একটু বিস্তারিত বলুন — কী সমস্যা?\n"
                    f"🛠️ Admin শীঘ্রই সমাধান দেবেন।\n\n"
                    f"{BOT_SIGNATURE}"
                ),
                "reply_to_message_id": msg_id
            })
        return

    # Problem details
    if sender_id and sender_id in problem_tracking:
        info = problem_tracking[sender_id]
        if info.get("waiting") and text:
            problem_tracking[sender_id]["waiting"] = False
            problem_text = text
            tg_api(token, "sendMessage", {
                "chat_id": owner_id,
                "text": (
                    f"🆘 নতুন সমস্যা রিপোর্ট!\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"👤 Member: {info['name']}\n"
                    f"💬 সমস্যা: {problem_text}\n"
                    f"🏠 Group ID: {chat_id}\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"⏰ ১০ মিনিটে reply না করলে auto msg যাবে\n"
                    f"✏️ Fix: /fix {sender_id} সমাধান"
                )
            })
            tg_api(token, "sendMessage", {
                "chat_id": chat_id,
                "text": (
                    f"✅ {info['name']} সমস্যা Admin কে জানানো হয়েছে!\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"⏳ শীঘ্রই সমাধান দেওয়া হবে।\n\n"
                    f"{BOT_SIGNATURE}"
                ),
                "reply_to_message_id": msg_id
            })
            pending_problems[sender_id] = {
                "chat_id": chat_id,
                "name": info["name"],
                "problem": problem_text,
                "time": datetime.now().timestamp()
            }
            del problem_tracking[sender_id]
            print(f"🆘 Problem: {sender_name} → {problem_text[:30]}")
        return

    # Owner mention
    if text and text.strip().endswith("?"):
        tg_api(token, "sendMessage", {
            "chat_id": chat_id,
            "text": (
                f"📢 [Admin](tg://user?id={owner_id}) একটু দেখুন!\n"
                f"💬 {sender_mention} প্রশ্ন করেছেন।"
            ),
            "parse_mode": "Markdown"
        })


def handle_owner_fix(token, msg, owner_id):
    text = msg.get("text", "")
    if not text.startswith("/fix"):
        return False
    parts = text.split(" ", 2)
    if len(parts) < 3:
        tg_api(token, "sendMessage", {"chat_id": owner_id,
            "text": "Format: /fix [user_id] [সমাধান]"})
        return True
    try:
        uid = int(parts[1])
        solution = parts[2]
    except ValueError:
        return False
    pending_problems.pop(uid, None)
    for gid in group_chat_ids:
        tg_api(token, "sendMessage", {
            "chat_id": gid,
            "parse_mode": "Markdown",
            "text": (
                f"╔══════════════════════╗\n"
                f"║   🛠️  PROBLEM SOLVED!    ║\n"
                f"╚══════════════════════╝\n\n"
                f"✅ [Member](tg://user?id={uid}) আপনার সমস্যার সমাধান:\n\n"
                f"💡 {solution}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"আর সমস্যা হলে জানাবেন! 😊\n\n"
                f"{BOT_SIGNATURE}"
            )
        })
    tg_api(token, "sendMessage", {"chat_id": owner_id, "text": "✅ Fix message পাঠানো হয়েছে!"})
    print(f"🛠️ Fix sent for user {uid}")
    return True


async def timeout_loop(token):
    while True:
        await asyncio.sleep(30)
        now = datetime.now().timestamp()
        for uid in [u for u, i in list(pending_problems.items())
                    if now - i["time"] >= OWNER_REPLY_TIMEOUT]:
            info = pending_problems.pop(uid, None)
            if not info:
                continue
            tg_api(token, "sendMessage", {
                "chat_id": info["chat_id"],
                "text": (
                    f"╔══════════════════════╗\n"
                    f"║   ⏰  AUTO REPLY          ║\n"
                    f"╚══════════════════════╝\n\n"
                    f"হ্যালো {info['name']}! 👋\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔴 Owner এখন busy আছেন\n"
                    f"⏳ আপনার সমস্যা noted হয়েছে\n"
                    f"🛠️ যত তাড়াতাড়ি সম্ভব fix হবে!\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"অপেক্ষার জন্য ধন্যবাদ! 🙏\n\n"
                    f"{BOT_SIGNATURE}"
                )
            })
            print(f"⏰ Auto reply (10min): {info['name']}")


async def reminder_loop(token):
    """প্রতি ঘণ্টায় (সকাল ৮:৩০ - রাত ৯:৩০) group এ reminder পাঠাও"""
    while True:
        now = datetime.now()
        # পরবর্তী পুরো ঘণ্টা পর্যন্ত wait করো
        next_hour = now.replace(minute=30, second=0, microsecond=0)
        if next_hour <= now:
            # পরের ঘণ্টার :৩০ তে
            next_hour = next_hour.replace(hour=now.hour + 1) if now.hour < 23 else next_hour.replace(
                hour=0) + timedelta(days=1)
        wait_sec = (next_hour - now).total_seconds()
        await asyncio.sleep(wait_sec)

        now = datetime.now()
        open_time = now.replace(hour=GROUP_OPEN_HOUR, minute=GROUP_OPEN_MINUTE, second=0, microsecond=0)
        close_time = now.replace(hour=GROUP_CLOSE_HOUR, minute=GROUP_CLOSE_MINUTE, second=0, microsecond=0)

        if group_chat_ids:
            # রাত ৯:৩০ → ঘুমের reminder
            if abs((now - close_time).total_seconds()) < 90:
                sleep_reminder = (
                    "╔══════════════════════╗\n"
                    "║   🌙  GOOD NIGHT!        ║\n"
                    "╚══════════════════════╝\n\n"
                    "হ্যালো সবাই! 👋 শুভ রাত্রি! 🌙\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "😴 Admin এখন ঘুমাতে যাচ্ছেন\n"
                    "🔒 Group এখন বন্ধ হচ্ছে\n"
                    "⏰ সকাল ৮:৩০ এ আবার চালু হবে\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    "❓ কারো কোনো সমস্যা থাকলে\n"
                    "💬 কাল সকালে জানাবেন\n"
                    "🛠️ সমাধান করে দেওয়া হবে!\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"{BOT_SIGNATURE}"
                )
                for gid in list(group_chat_ids):
                    tg_api(token, "sendMessage", {"chat_id": gid, "text": sleep_reminder})
                print("🌙 Sleep reminder sent")

            # সকাল ৮:৩০ - রাত ৯:৩০ এর মধ্যে → normal reminder
            elif open_time <= now < close_time:
                for gid in list(group_chat_ids):
                    tg_api(token, "sendMessage", {"chat_id": gid, "text": REMINDER_MESSAGE})
                print(f"🔔 Hourly reminder sent: {now.strftime('%H:%M')}")


async def group_lock_unlock_loop(token):
    """রাত ৯:৩০ এ group lock, সকাল ৮:৩০ এ unlock
    Owner আগে open করলেও bot বন্ধ করে দেবে"""
    group_was_locked = False  # track করো group locked আছে কিনা

    while True:
        await asyncio.sleep(30)
        now = datetime.now()
        open_time = now.replace(hour=GROUP_OPEN_HOUR, minute=GROUP_OPEN_MINUTE, second=0, microsecond=0)
        close_time = now.replace(hour=GROUP_CLOSE_HOUR, minute=GROUP_CLOSE_MINUTE, second=0, microsecond=0)

        is_night = not (open_time <= now < close_time)  # রাতের সময়

        if is_night and not group_was_locked:
            # রাতের সময় → lock করো
            for gid in list(group_chat_ids):
                result = tg_api(token, "setChatPermissions", {
                    "chat_id": gid,
                    "permissions": {
                        "can_send_messages": False,
                        "can_send_audios": False,
                        "can_send_documents": False,
                        "can_send_photos": False,
                        "can_send_videos": False,
                        "can_send_video_notes": False,
                        "can_send_voice_notes": False,
                        "can_send_polls": False,
                        "can_send_other_messages": False,
                        "can_add_web_page_previews": False
                    }
                })
                if result.get("ok"):
                    print(f"🔒 Group locked: {gid}")
            group_was_locked = True

        elif not is_night and group_was_locked:
            # সকালের সময় → unlock করো
            open_msg = (
                "╔══════════════════════╗\n"
                "║   🌅  GOOD MORNING!      ║\n"
                "╚══════════════════════╝\n\n"
                "হ্যালো সবাই! 👋 শুভ সকাল! ☀️\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🔓 Group আবার চালু হয়েছে!\n"
                "✅ Admin এখন active আছেন\n"
                "💬 এখন message করতে পারবেন\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "❓ কারো কোনো সমস্যা আছে?\n"
                "💬 নির্দ্বিধায় জানান\n"
                "🛠️ সমাধান করে দেওয়া হবে!\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"{BOT_SIGNATURE}"
            )
            for gid in list(group_chat_ids):
                result = tg_api(token, "setChatPermissions", {
                    "chat_id": gid,
                    "permissions": {
                        "can_send_messages": True,
                        "can_send_audios": True,
                        "can_send_documents": True,
                        "can_send_photos": True,
                        "can_send_videos": True,
                        "can_send_video_notes": True,
                        "can_send_voice_notes": False,
                        "can_send_polls": True,
                        "can_send_other_messages": True,
                        "can_add_web_page_previews": True
                    }
                })
                if result.get("ok"):
                    tg_api(token, "sendMessage", {"chat_id": gid, "text": open_msg})
                    print(f"🔓 Group unlocked: {gid}")
            group_was_locked = False


async def welcome_bot_loop():
    if not WELCOME_BOT_TOKEN:
        print("⚠️ WELCOME_BOT_TOKEN নেই")
        return
    print("🎉 Welcome Bot চালু!")
    print("🚫 Bad word filter চালু!")
    print("🗑️ Voice delete চালু!")
    print("🆘 Problem tracking চালু!")
    print("⏰ 10min timeout চালু!")
    print("🔔 5hr reminder চালু!")

    tg_api(WELCOME_BOT_TOKEN, "getUpdates", {"offset": -1, "limit": 1, "timeout": 0})
    await asyncio.sleep(2)

    asyncio.create_task(reminder_loop(WELCOME_BOT_TOKEN))
    asyncio.create_task(timeout_loop(WELCOME_BOT_TOKEN))
    asyncio.create_task(group_lock_unlock_loop(WELCOME_BOT_TOKEN))

    offset = 0
    while True:
        try:
            result = tg_api(WELCOME_BOT_TOKEN, "getUpdates", {
                "offset": offset,
                "timeout": 5,
                "allowed_updates": ["message", "chat_member"]
            })
            if not result.get("ok"):
                await asyncio.sleep(3)
                continue
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message")
                if msg:
                    ctype = msg.get("chat", {}).get("type", "")
                    sid = msg.get("from", {}).get("id")
                    if ctype == "private" and sid == OWNER_ID:
                        if not handle_owner_fix(WELCOME_BOT_TOKEN, msg, OWNER_ID):
                            if msg.get("text") == "/start":
                                tg_api(WELCOME_BOT_TOKEN, "sendMessage", {
                                    "chat_id": msg["chat"]["id"],
                                    "text": (
                                        "╔══════════════════╗\n"
                                        "║  🤖 Bot চালু!        ║\n"
                                        "╚══════════════════╝\n\n"
                                        "✅ সব feature চালু:\n"
                                        "🎉 Welcome message\n"
                                        "🚫 Bad word filter\n"
                                        "🗑️ Voice delete\n"
                                        "🆘 Problem tracking\n"
                                        "⏰ 10min auto-reply\n"
                                        "🔔 5hr reminder\n\n"
                                        "🛠️ Fix format:\n"
                                        "/fix [user_id] [সমাধান]\n\n"
                                        f"{BOT_SIGNATURE}"
                                    )
                                })
                    elif ctype in ["group", "supergroup"]:
                        handle_group_message(WELCOME_BOT_TOKEN, msg, OWNER_ID)
                cm = update.get("chat_member")
                if cm:
                    os_ = cm["old_chat_member"]["status"]
                    ns = cm["new_chat_member"]["status"]
                    if os_ in ["left", "kicked"] and ns in ["member", "administrator", "creator"]:
                        member = cm["new_chat_member"]["user"]
                        cid = cm["chat"]["id"]
                        group_chat_ids.add(cid)
                        first = member.get("first_name", "")
                        last = member.get("last_name", "")
                        full_name = (first + " " + last).strip() or "বন্ধু"
                        username = member.get("username", "")
                        name = f"@{username}" if username else full_name
                        tg_api(WELCOME_BOT_TOKEN, "sendMessage", {
                            "chat_id": cid,
                            "text": WELCOME_MESSAGE.format(name=name)
                        })
                        print(f"🎉 Welcome: {full_name}")
        except Exception as e:
            print(f"⚠️ Loop error: {e}")
        await asyncio.sleep(1)


# ============================================================
# 🚀 MAIN
# ============================================================
async def main():
    print("🚀 Userbot চালু হচ্ছে...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Login: {me.first_name} (@{me.username})")
    print("📨 Auto-reply চালু!")
    print("🌞 সকাল ৮:৩০ - রাত ৯:৩০ → Busy message")
    print("🌙 রাত ৯:৩০ এর পরে → Sleep message")
    print("💡 ৫ মিনিট idle → bot আবার চালু")
    await asyncio.gather(
        client.run_until_disconnected(),
        welcome_bot_loop()
    )


if __name__ == "__main__":
    asyncio.run(main())
