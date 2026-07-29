import asyncio
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
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

# ============================================================
# 🚫 BAD WORDS LIST (বাংলা + ইংরেজি)
# ============================================================
BAD_WORDS = [
    # বাংলা গালি
    "মাদারচোদ", "মাদারচুদ", "বাল", "বালছাল", "চোদ", "চুদ", "চুদি",
    "শালা", "হারামি", "হারামজাদা", "কুত্তা", "কুত্তার বাচ্চা",
    "বেশ্যা", "রান্ডি", "খানকি", "মাগি", "ভোদা", "ভোদাই",
    "গাধা", "গু", "হিজড়া", "শুয়োর", "শুয়োরের বাচ্চা",
    "কামিনী", "ছিনাল", "বজ্জাত", "নোংরা",
    # ইংরেজি গালি
    "fuck", "fucker", "fucking", "fuk", "f*ck",
    "shit", "bitch", "bastard", "asshole", "ass",
    "dick", "cock", "pussy", "whore", "slut",
    "cunt", "nigga", "nigger", "motherfucker",
    "idiot", "stupid", "moron", "dumb",
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
    "『 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗦𝗵𝗮𝗺𝗶𝗺 𝗕𝗼𝘁 🤖 』"
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
    "⏰ আগামীকাল সকাল ১০টায়\n"
    "   আপনাকে reply দেওয়া হবে\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "🌟 শুভ রাত্রি! ভালো থাকুন 🙏\n\n"
    "『 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗦𝗵𝗮𝗺𝗶𝗺 𝗕𝗼𝘁 🤖 』"
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
    "『 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗦𝗵𝗮𝗺𝗶𝗺 𝗕𝗼𝘁 🤖 』"
)

WAIT_SECONDS = 300

# ============================================================
# 🤖 USERBOT CLIENT
# ============================================================
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("shamim_userbot", API_ID, API_HASH)

owner_replied: set = set()
idle_timers: dict = {}


def get_auto_reply():
    hour = datetime.now().hour
    if 10 <= hour < 22:
        return BUSY_MESSAGE
    return SLEEP_MESSAGE


def contains_bad_word(text: str) -> bool:
    """Text এ bad word আছে কিনা চেক করো"""
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
# 📨 PRIVATE MESSAGE HANDLERS (userbot)
# ============================================================
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def incoming_handler(event):
    sender = await event.get_sender()
    sender_id = sender.id
    if sender.bot:
        return
    if sender_id in owner_replied:
        return
    reply_msg = get_auto_reply()
    hour = datetime.now().hour
    mode = "🌞 Day" if 10 <= hour < 22 else "🌙 Sleep"
    await event.reply(reply_msg)
    print(f"✅ Auto-replied [{mode}]: {sender.first_name} [ID: {sender_id}]")


@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def outgoing_handler(event):
    chat = await event.get_chat()
    receiver_id = chat.id
    owner_replied.add(receiver_id)
    reset_idle_timer(receiver_id)
    print(f"🔕 Bot বন্ধ + timer: [{receiver_id}]")


# ============================================================
# 🎉 WELCOME BOT — urllib দিয়ে
# ============================================================
def tg_api(token, method, data):
    url = f"https://api.telegram.org/bot{token}/{method}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"⚠️ API error [{method}]: {e}")
        return {}


def handle_group_message(token, msg, owner_id):
    """Group message handle — bad word delete + voice delete + unanswered alert"""
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    chat_type = chat.get("type", "")

    # শুধু group এ কাজ করবে
    if chat_type not in ["group", "supergroup"]:
        return

    msg_id = msg.get("message_id")
    sender = msg.get("from", {})
    sender_name = sender.get("first_name", "কেউ")
    sender_username = sender.get("username", "")
    sender_mention = f"@{sender_username}" if sender_username else sender_name

    text = msg.get("text", "") or msg.get("caption", "") or ""

    # ── ১. Voice message delete ──
    if msg.get("voice") or msg.get("video_note"):
        tg_api(token, "deleteMessage", {
            "chat_id": chat_id,
            "message_id": msg_id
        })
        tg_api(token, "sendMessage", {
            "chat_id": chat_id,
            "text": (
                f"🚫 {sender_mention} এর voice message delete করা হয়েছে!\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"⚠️ এই group এ voice message পাঠানো নিষিদ্ধ।\n"
                f"💬 Text এ লিখুন।"
            )
        })
        print(f"🗑️ Voice deleted: {sender_name} → {chat.get('title')}")
        return

    # ── ২. Bad word delete ──
    if contains_bad_word(text):
        tg_api(token, "deleteMessage", {
            "chat_id": chat_id,
            "message_id": msg_id
        })
        tg_api(token, "sendMessage", {
            "chat_id": chat_id,
            "text": (
                f"⛔ {sender_mention} এর message delete করা হয়েছে!\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🚫 অশ্লীল বা খারাপ শব্দ ব্যবহার নিষিদ্ধ।\n"
                f"✅ সবার সাথে ভদ্রভাবে কথা বলুন।"
            )
        })
        print(f"🗑️ Bad word deleted: {sender_name} → {chat.get('title')}")
        return

    # ── ৩. Unanswered message → owner কে mention ──
    # যদি কেউ question করে (? দিয়ে শেষ) বা help চায়
    if text and (text.strip().endswith("?") or
                 any(w in text.lower() for w in ["help", "হেল্প", "সাহায্য", "সমস্যা", "problem", "plm", "pls", "please"])):
        # owner কে mention করো
        owner_mention = f"[Admin](tg://user?id={owner_id})"
        tg_api(token, "sendMessage", {
            "chat_id": chat_id,
            "text": (
                f"📢 {owner_mention} একটু দেখুন!\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"💬 {sender_mention} সাহায্য চাইছেন।"
            ),
            "parse_mode": "Markdown"
        })
        print(f"📢 Owner mentioned for: {sender_name} → {text[:30]}")


async def welcome_bot_loop():
    if not WELCOME_BOT_TOKEN:
        print("⚠️ WELCOME_BOT_TOKEN নেই — Welcome bot বন্ধ")
        return

    print("🎉 Welcome Bot চালু হয়েছে!")
    print("🚫 Bad word filter চালু!")
    print("🗑️ Voice message delete চালু!")
    print("📢 Owner mention system চালু!")
    offset = 0
    base = f"https://api.telegram.org/bot{WELCOME_BOT_TOKEN}"

    while True:
        try:
            url = (
                f"{base}/getUpdates"
                f"?offset={offset}&timeout=30"
                f"&allowed_updates=%5B%22message%22%2C%22chat_member%22%5D"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read())

            if not data.get("ok"):
                await asyncio.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                msg = update.get("message")
                if msg:
                    chat_type = msg.get("chat", {}).get("type", "")

                    # /start command (private)
                    if msg.get("text") == "/start" and chat_type == "private":
                        tg_api(WELCOME_BOT_TOKEN, "sendMessage", {
                            "chat_id": msg["chat"]["id"],
                            "text": (
                                "╔══════════════════╗\n"
                                "║  🤖 Shamim Bot চালু!  ║\n"
                                "╚══════════════════╝\n\n"
                                "✅ সব feature চালু আছে:\n"
                                "🎉 Welcome message\n"
                                "🚫 Bad word filter\n"
                                "🗑️ Voice message delete\n"
                                "📢 Owner mention system"
                            )
                        })

                    # Group message handle
                    elif chat_type in ["group", "supergroup"]:
                        handle_group_message(WELCOME_BOT_TOKEN, msg, OWNER_ID)

                # নতুন member join
                cm = update.get("chat_member")
                if cm:
                    old_s = cm["old_chat_member"]["status"]
                    new_s = cm["new_chat_member"]["status"]
                    was_out = old_s in ["left", "kicked"]
                    is_in = new_s in ["member", "administrator", "creator"]

                    if was_out and is_in:
                        member = cm["new_chat_member"]["user"]
                        chat_id = cm["chat"]["id"]
                        first = member.get("first_name", "")
                        last = member.get("last_name", "")
                        full_name = (first + " " + last).strip() or "বন্ধু"
                        username = member.get("username", "")
                        name = f"@{username}" if username else full_name
                        tg_api(WELCOME_BOT_TOKEN, "sendMessage", {
                            "chat_id": chat_id,
                            "text": WELCOME_MESSAGE.format(name=name)
                        })
                        print(f"🎉 Welcome: {full_name} → {cm['chat']['title']}")

        except Exception as e:
            print(f"⚠️ Welcome loop error: {e}")

        await asyncio.sleep(1)


# ============================================================
# 🚀 MAIN
# ============================================================
async def main():
    print("🚀 Userbot চালু হচ্ছে...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Login সফল! Account: {me.first_name} (@{me.username})")
    print("📨 Auto-reply চালু!")
    print("🌞 সকাল ১০টা - রাত ১০টা → Busy message")
    print("🌙 রাত ১০টার পরে → Sleep message")
    print("💡 ৫ মিনিট idle → bot আবার চালু")

    await asyncio.gather(
        client.run_until_disconnected(),
        welcome_bot_loop()
    )


if __name__ == "__main__":
    asyncio.run(main())
