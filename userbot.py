import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

# ============================
# Configuration
# ============================
API_ID = int(os.getenv("API_ID", "35398542"))
API_HASH = os.getenv("API_HASH", "e7991fac34e488dbc41f95125a778cfa")
SESSION_STRING = os.getenv("SESSION_STRING", "")

AUTO_REPLY_MESSAGE = (
    "👋 হ্যালো! আপনার message পেয়েছি।\n\n"
    "😊 Owner এখন একটু busy আছেন।\n"
    "⏰ ৫-১০ মিনিটের মধ্যে আপনাকে reply করবেন।\n\n"
    "অপেক্ষার জন্য ধন্যবাদ! 🙏"
)

# প্রতি user কে একবারই reply (spam এড়াতে)
replied_users: set = set()

# ============================
# Session setup
# ============================
if SESSION_STRING:
    # Railway তে string session ব্যবহার করবে
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    # Local এ file session ব্যবহার করবে
    client = TelegramClient("shamim_userbot", API_ID, API_HASH)


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply_handler(event):
    sender = await event.get_sender()
    sender_id = sender.id

    # Bot থেকে আসা message ignore করো
    if sender.bot:
        return

    # প্রতিটা message এ reply করো
    if sender_id not in replied_users:
        replied_users.add(sender_id)
        await event.reply(AUTO_REPLY_MESSAGE)
        print(f"✅ Auto-replied to: {sender.first_name} (@{sender.username}) [ID: {sender_id}]")


async def main():
    print("🚀 Userbot চালু হচ্ছে...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Login সফল! Account: {me.first_name} (@{me.username})")

    # SESSION_STRING না থাকলে generate করে দেখাও
    if not SESSION_STRING:
        session_str = client.session.save()
        print("\n" + "="*60)
        print("📋 আপনার SESSION_STRING (Railway তে লাগবে):")
        print(session_str)
        print("="*60 + "\n")

    print("📨 Auto-reply চালু আছে। কেউ message করলে reply যাবে।")
    print("বন্ধ করতে Ctrl+C চাপুন।")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
