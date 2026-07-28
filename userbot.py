import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "35398542"))
API_HASH = os.getenv("API_HASH", "e7991fac34e488dbc41f95125a778cfa")
SESSION_STRING = os.getenv("SESSION_STRING", "")

AUTO_REPLY_MESSAGE = (
    "👋 হ্যালো! আপনার message পেয়েছি।\n\n"
    "😊 Owner এখন একটু busy আছেন।\n"
    "⏰ ৫-১০ মিনিটের মধ্যে আপনাকে reply করবেন।\n\n"
    "অপেক্ষার জন্য ধন্যবাদ! 🙏"
)

WAIT_SECONDS = 60

if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("shamim_userbot", API_ID, API_HASH)

owner_replied: set = set()
idle_timers: dict = {}

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

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def incoming_handler(event):
    sender = await event.get_sender()
    sender_id = sender.id
    if sender.bot:
        return
    if sender_id in owner_replied:
        print(f"⏸ Bot বন্ধ: {sender.first_name} [ID: {sender_id}]")
        return
    await event.reply(AUTO_REPLY_MESSAGE)
    print(f"✅ Auto-replied: {sender.first_name} [ID: {sender_id}]")

@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def outgoing_handler(event):
    chat = await event.get_chat()
    receiver_id = chat.id
    owner_replied.add(receiver_id)
    reset_idle_timer(receiver_id)
    print(f"🔕 Bot বন্ধ + 1 min timer: [{receiver_id}]")

async def main():
    print("🚀 Userbot চালু হচ্ছে...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Login: {me.first_name} (@{me.username})")
    print("📨 Auto-reply চালু!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
