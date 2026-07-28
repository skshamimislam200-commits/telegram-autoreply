"""
╔══════════════════════════════════════╗
║        🎉 WELCOME BOT 🎉             ║
║  Group এ নতুন member আসলে welcome    ║
║  message পাঠাবে এই bot               ║
╚══════════════════════════════════════╝

📌 Setup:
   1. @BotFather থেকে নতুন bot বানান
   2. .env ফাইলে WELCOME_BOT_TOKEN= দিন
   3. Bot কে group এ add করুন
   4. Bot কে group Admin করুন
   5. চালান: python welcome_bot.py
"""

import logging
import os
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.ext import (
    Application,
    ChatMemberHandler,
    ContextTypes,
    CommandHandler,
)
from dotenv import load_dotenv

load_dotenv()

# ============================
# ⚙️ Configuration
# ============================
WELCOME_BOT_TOKEN = os.getenv("WELCOME_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ============================
# 🎨 Welcome Message
# (নিজের মতো customize করুন)
# ============================
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

# ============================
# Logging setup
# ============================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============================
# Member join check helper
# ============================
def member_joined(update: ChatMemberUpdated) -> bool:
    """নতুন member join করেছে কিনা চেক করো"""
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    # আগে ছিল না বা banned/left ছিল, এখন member/admin হয়েছে
    was_out = old_status in [
        ChatMember.LEFT,
        ChatMember.BANNED,
    ]
    is_in = new_status in [
        ChatMember.MEMBER,
        ChatMember.ADMINISTRATOR,
        ChatMember.OWNER,
    ]
    return was_out and is_in


# ============================
# Welcome handler
# ============================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """নতুন member join করলে welcome message পাঠাও"""
    result = update.chat_member

    if not member_joined(result):
        return

    member = result.new_chat_member.user
    chat = result.chat

    # নতুন member এর নাম
    if member.username:
        name = f"@{member.username}"
    else:
        name = member.full_name

    # Welcome message পাঠাও
    welcome_text = WELCOME_MESSAGE.format(name=name)
    await context.bot.send_message(chat_id=chat.id, text=welcome_text)

    logger.info(f"✅ Welcome পাঠানো হয়েছে: {member.full_name} → {chat.title}")


# ============================
# /start command
# ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "╔══════════════════╗\n"
        "║  🎉 Welcome Bot চালু!  ║\n"
        "╚══════════════════╝\n\n"
        "✅ Bot সফলভাবে চালু আছে!\n\n"
        "📌 এই bot এর কাজ:\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔹 Group এ add করুন\n"
        "🔹 Admin বানান\n"
        "🔹 নতুন member আসলে\n"
        "   automatically welcome\n"
        "   message যাবে!\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "『 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗦𝗵𝗮𝗺𝗶𝗺 𝗕𝗼𝘁 🤖 』"
    )


# ============================
# /setwelcome command (owner only)
# ============================
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Owner welcome message দেখতে পারবেন"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ এই command শুধু owner ব্যবহার করতে পারবেন।")
        return
    preview = WELCOME_MESSAGE.format(name="@example_user")
    await update.message.reply_text(
        f"📋 বর্তমান Welcome Message:\n\n{preview}"
    )


# ============================
# Main function
# ============================
def main() -> None:
    if not WELCOME_BOT_TOKEN:
        print("❌ WELCOME_BOT_TOKEN পাওয়া যায়নি!")
        print("👉 .env ফাইলে এই line যোগ করুন:")
        print("   WELCOME_BOT_TOKEN=আপনার_bot_token_এখানে")
        print("\n📌 @BotFather থেকে নতুন bot বানিয়ে token নিন")
        return

    app = Application.builder().token(WELCOME_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setwelcome", setwelcome))

    # Group member join event
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    logger.info("🎉 Welcome Bot চালু হয়েছে!")
    logger.info("📌 Group এ add করুন এবং Admin বানান")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
