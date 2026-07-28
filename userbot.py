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

# ============================
# Session setup
# ============================
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("shamim_userbot", API_ID, API_HASH)

# যাদের সাথে owner reply করেছেন — তাদের জন্য bot বন্ধ
owner_replied: set = set()


# ============================
# কেউ owner কে message করলে
# ============================
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def incoming_message_handler(event):
    sender = await event.get_sender()
    sender_id = sender.id

    # Bot থেকে আসা message ignore
    if sender.bot:
        return

    # Owner এই user কে reply করেছেন → bot বন্ধ আছে
    if sender_id in owner_replied:
        print(f"⏸ Bot বন্ধ (owner replied): {sender.first_name} [ID: {sender_id}]")
        return

    # Bot চালু → reply দাও
    await event.reply(AUTO_REPLY_MESSAGE)
    print(f"✅ Auto-replied: {sender.first_name} (@{sender.username}) [ID: {sender_id}]")


# ============================
# Owner কাউকে reply করলে
# সেই user এর জন্য bot বন্ধ হবে
# ============================
@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def outgoing_message_handler(event):
    chat = await event.get_chat()
    receiver_id = chat.id

    if receiver_id not in owner_replied:
        owner_replied.add(receiver_id)
        print(f"🔕 Bot বন্ধ হলো: owner replied to [{receiver_id}]")


# ============================
# Main
# ============================
async def main():
    print("🚀 Userbot চালু হচ্ছে...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Login সফল! Account: {me.first_name} (@{me.username})")
    print("📨 Auto-reply চালু।")
    print("💡 আপনি কাউকে reply করলে তার জন্য bot বন্ধ হবে।")
    print("বন্ধ করতে Ctrl+C চাপুন।")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
