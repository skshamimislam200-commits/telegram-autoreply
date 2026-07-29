import asyncio
import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "35398542"))
API_HASH = os.getenv("API_HASH", "e7991fac34e488dbc41f95125a778cfa")
SESSION_STRING = os.getenv("SESSION_STRING", "")
WELCOME_BOT_TOKEN = os.getenv("WELCOME_BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "7918793670"))

GROUP_REMINDER_INTERVAL = 5 * 60 * 60
OWNER_REPLY_TIMEOUT = 10 * 60

BOT_SIGNATURE = "[ MD SHAMIM ISLAM ]"

BAD_WORDS = [
    "madarchod", "madarjat", "bal", "balchal", "chod", "chud", "chudi",
    "harami", "haramjada", "kuttar bacha", "beshsha", "khankir", "magi",
    "hijra", "shuorer bacha", "gadha", "sala", "shala",
    "madarchod", "fuck", "fucker", "fucking", "fuk", "f*ck",
    "shit", "bitch", "bastard", "asshole", "ass", "arse",
    "dick", "cock", "pussy", "whore", "slut", "cunt",
    "nigga", "nigger", "motherfucker", "mf", "idiot", "stupid",
    "moron", "dumb", "loser", "wtf", "stfu", "gtfo", "kys",
]

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
    "🕐 ৩০ - ৬০ মিনিটের মধ্যে reply হবে\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "💙 ধৈর্য ধরার জন্য ধন্যবাদ! 🙏\n\n"
    "[ MD SHAMIM ISLAM ]"
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
    "⏰ আগামীকাল সকাল ১০টায় reply হবে\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "🌟 শুভ রাত্রি! 🙏\n\n"
    "[ MD SHAMIM ISLAM ]"
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
    "│  💬 সমস্যায় admin দের সাথে যোগাযোগ │\n"
    "└──────────────────────────┘\n\n"
    "আশা করি এখানে ভালো লাগবে! 😊\n\n"
    "[ MD SHAMIM ISLAM ]"
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
    "[ MD SHAMIM ISLAM ]"
)

WAIT_SECONDS = 300

if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("shamim_userbot", API_ID, API_HASH)

owner_replied: set = set()
idle_timers: dict = {}
problem_tracking: dict = {}
pending_problems: dict = {}
group_chat_ids: set = set()


def get_auto_reply():
    hour = datetime.now().hour
    if 10 <= hour < 22:
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
    print(f"Bot again active: [{user_id}]")


def reset_idle_timer(user_id):
    if user_id in idle_timers:
        idle_timers[user_id].cancel()
    task = asyncio.create_task(reactivate_bot(user_id))
    idle_timers[user_id] = task


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def incoming_handler(event):
    sender = await event.get_sender()
    sender_id = sender.id
    if sender.bot:
        return
    if sender_id in owner_replied:
        return
    await event.reply(get_auto_reply())
    print(f"Auto-replied: {sender.first_name} [{sender_id}]")


@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def outgoing_handler(event):
    chat = await event.get_chat()
    owner_replied.add(chat.id)
    reset_idle_timer(chat.id)
    print(f"Bot off + timer: [{chat.id}]")


def tg_api(token, method, data):
    url = f"https://api.telegram.org/bot{token}/{method}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"API error [{method}]: {e}")
        return {}


def handle_group_message(token, msg, owner_id):
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    if chat.get("type") not in ["group", "supergroup"]:
        return
    group_chat_ids.add(chat_id)
    msg_id = msg.get("message_id")
    sender = msg.get("from", {})
    sender_id = sender.get("id")
    sender_name = sender.get("first_name", "Member")
    uname = sender.get("username", "")
    mention = f"@{uname}" if uname else sender_name
    text = msg.get("text", "") or msg.get("caption", "") or ""

    if msg.get("voice") or msg.get("video_note"):
        tg_api(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
        tg_api(token, "sendMessage", {"chat_id": chat_id, "text": (
            f"🚫 {mention} এর voice message delete!\n"
            f"Voice message নিষিদ্ধ। Text এ লিখুন।\n\n{BOT_SIGNATURE}"
        )})
        return

    if contains_bad_word(text):
        tg_api(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
        tg_api(token, "sendMessage", {"chat_id": chat_id, "text": (
            f"⛔ {mention} এর message delete!\n"
            f"অশ্লীল শব্দ নিষিদ্ধ। ভদ্রভাবে কথা বলুন।\n\n{BOT_SIGNATURE}"
        )})
        return

    problem_kw = ["সমস্যা", "problem", "plm", "help", "হেল্প", "সাহায্য",
                  "pls", "please", "issue", "fix", "কাজ করছে না", "হচ্ছে না"]
    if any(w in text.lower() for w in problem_kw) and sender_id:
        if sender_id not in problem_tracking:
            problem_tracking[sender_id] = {
                "chat_id": chat_id, "name": mention,
                "waiting": True, "msg_id": msg_id,
                "time": datetime.now().timestamp()
            }
            tg_api(token, "sendMessage", {"chat_id": chat_id,
                "reply_to_message_id": msg_id, "text": (
                f"🤝 {mention} সমস্যার কথা শুনলাম!\n"
                f"বিস্তারিত বলুন — কী সমস্যা?\n\n{BOT_SIGNATURE}"
            )})
        return

    if sender_id and sender_id in problem_tracking:
        info = problem_tracking[sender_id]
        if info.get("waiting") and text:
            problem_tracking[sender_id]["waiting"] = False
            tg_api(token, "sendMessage", {"chat_id": owner_id, "text": (
                f"New Problem Report!\n"
                f"Member: {info['name']}\n"
                f"Problem: {text}\n"
                f"Group: {chat_id}\n\n"
                f"10 min reply না করলে bot auto msg দেবে।\n"
                f"Fix: /fix {sender_id} [solution]"
            )})
            tg_api(token, "sendMessage", {"chat_id": chat_id,
                "reply_to_message_id": msg_id, "text": (
                f"✅ {info['name']} সমস্যা Admin কে জানানো হয়েছে!\n"
                f"শীঘ্রই সমাধান দেওয়া হবে।\n\n{BOT_SIGNATURE}"
            )})
            pending_problems[sender_id] = {
                "chat_id": chat_id, "name": info["name"],
                "problem": text, "time": datetime.now().timestamp()
            }
            del problem_tracking[sender_id]
        return

    if text and text.strip().endswith("?"):
        tg_api(token, "sendMessage", {"chat_id": chat_id,
            "parse_mode": "Markdown",
            "text": f"[Admin](tg://user?id={owner_id}) একটু দেখুন!\n{mention} প্রশ্ন করেছেন।"
        })


def handle_owner_fix(token, msg, owner_id):
    text = msg.get("text", "")
    if not text.startswith("/fix"):
        return False
    parts = text.split(" ", 2)
    if len(parts) < 3:
        tg_api(token, "sendMessage", {"chat_id": owner_id,
            "text": "Format: /fix [user_id] [solution]"})
        return True
    try:
        uid = int(parts[1])
        solution = parts[2]
    except ValueError:
        return False
    pending_problems.pop(uid, None)
    for gid in group_chat_ids:
        tg_api(token, "sendMessage", {"chat_id": gid, "parse_mode": "Markdown", "text": (
            f"PROBLEM SOLVED!\n\n"
            f"[Member](tg://user?id={uid}) আপনার সমস্যার সমাধান:\n\n"
            f"💡 {solution}\n\n"
            f"আর সমস্যা হলে জানাবেন!\n\n{BOT_SIGNATURE}"
        )})
    tg_api(token, "sendMessage", {"chat_id": owner_id, "text": "Fix message sent!"})
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
            tg_api(token, "sendMessage", {"chat_id": info["chat_id"], "text": (
                f"হ্যালো {info['name']}!\n\n"
                f"Owner এখন busy। সমস্যা noted হয়েছে।\n"
                f"যত তাড়াতাড়ি সম্ভব fix হবে!\n\n"
                f"ধন্যবাদ! 🙏\n\n{BOT_SIGNATURE}"
            )})
            print(f"Auto reply (10min): {info['name']}")


async def reminder_loop(token):
    await asyncio.sleep(GROUP_REMINDER_INTERVAL)
    while True:
        for gid in list(group_chat_ids):
            tg_api(token, "sendMessage", {"chat_id": gid, "text": REMINDER_MESSAGE})
        await asyncio.sleep(GROUP_REMINDER_INTERVAL)


async def welcome_bot_loop():
    if not WELCOME_BOT_TOKEN:
        print("WELCOME_BOT_TOKEN missing")
        return
    print("Welcome Bot running!")
    tg_api(WELCOME_BOT_TOKEN, "getUpdates", {"offset": -1, "limit": 1, "timeout": 0})
    await asyncio.sleep(2)
    asyncio.create_task(reminder_loop(WELCOME_BOT_TOKEN))
    asyncio.create_task(timeout_loop(WELCOME_BOT_TOKEN))
    offset = 0
    while True:
        try:
            result = tg_api(WELCOME_BOT_TOKEN, "getUpdates", {
                "offset": offset, "timeout": 5,
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
                                        "MD SHAMIM ISLAM Bot\n\n"
                                        "Features:\n"
                                        "Welcome / Bad word filter\n"
                                        "Voice delete / Problem tracking\n"
                                        "10min auto-reply / 5hr reminder\n\n"
                                        "Fix: /fix [user_id] [solution]\n\n"
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
                        fn = (member.get("first_name","")+" "+member.get("last_name","")).strip() or "Friend"
                        un = member.get("username","")
                        name = f"@{un}" if un else fn
                        tg_api(WELCOME_BOT_TOKEN, "sendMessage", {
                            "chat_id": cid,
                            "text": WELCOME_MESSAGE.format(name=name)
                        })
                        print(f"Welcome: {fn}")
        except Exception as e:
            print(f"Loop error: {e}")
        await asyncio.sleep(1)


async def main():
    print("Userbot starting...")
    await client.start()
    me = await client.get_me()
    print(f"Login: {me.first_name} (@{me.username})")
    await asyncio.gather(client.run_until_disconnected(), welcome_bot_loop())


if __name__ == "__main__":
    asyncio.run(main())
