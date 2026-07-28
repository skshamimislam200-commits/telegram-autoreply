import asyncio
import os
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "35398542"))
API_HASH = os.getenv("API_HASH", "e7991fac34e488dbc41f95125a778cfa")
SESSION_STRING = os.getenv("SESSION_STRING", "")

# ── দিনের বেলার message (সকাল ১০টা - রাত ১০টা) ──
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

# ── রাতের message (রাত ১০টার পরে) ──
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

WAIT_SECONDS = 300  # কথা বলার পর ৫ মিনিট idle থাকলে bot আবার চালু

if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("shamim_userbot", API_ID, API_HASH)

# owner যাদের সাথে কথা বলছেন (bot বন্ধ)
owner_replied: set = set()

# idle timer — owner ৫ মিনিট reply না করলে bot আবার চালু হবে
idle_timers: dict = {}


def get_auto_reply():
    """সময় অনুযায়ী সঠিক message বেছে দাও"""
    hour = datetime.now().hour  # local time
    # সকাল ১০টা (10) থেকে রাত ১০টা (22) পর্যন্ত → busy message
    if 10 <= hour < 22:
        return BUSY_MESSAGE
    else:
        # রাত ১০টার পরে বা সকাল ১০টার আগে → sleep message
        return SLEEP_MESSAGE


async def reactivate_bot(user_id):
    """৫ মিনিট পরে bot আবার চালু করবে"""
    await asyncio.sleep(WAIT_SECONDS)
    owner_replied.discard(user_id)
    idle_timers.pop(user_id, None)
    print(f"🔔 Bot আবার চালু: [{user_id}] (5 min idle)")


def reset_idle_timer(user_id):
    """Timer reset করো — owner আবার reply করলে timer নতুন করে শুরু"""
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

    # bot বন্ধ আছে এই user এর জন্য → চুপ থাকো
    if sender_id in owner_replied:
        print(f"⏸ Bot বন্ধ: {sender.first_name} [ID: {sender_id}]")
        return

    # সময় অনুযায়ী message নির্বাচন করো
    reply_msg = get_auto_reply()
    hour = datetime.now().hour
    mode = "🌞 Day" if 10 <= hour < 22 else "🌙 Sleep"

    await event.reply(reply_msg)
    print(f"✅ Auto-replied [{mode}]: {sender.first_name} (@{sender.username}) [ID: {sender_id}]")


@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def outgoing_handler(event):
    chat = await event.get_chat()
    receiver_id = chat.id

    # owner reply করলে → bot বন্ধ করো
    owner_replied.add(receiver_id)

    # idle timer শুরু করো — ৫ মিনিট পরে bot আবার চালু হবে
    reset_idle_timer(receiver_id)
    print(f"🔕 Bot বন্ধ + timer শুরু: [{receiver_id}]")


async def main():
    print("🚀 Userbot চালু হচ্ছে...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Login সফল! Account: {me.first_name} (@{me.username})")
    print("📨 Auto-reply চালু!")
    print("🌞 সকাল ১০টা - রাত ১০টা → Busy message")
    print("🌙 রাত ১০টার পরে → Sleep message")
    print("💡 আপনি reply করলে bot বন্ধ → ৫ মিনিট idle থাকলে আবার চালু")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
