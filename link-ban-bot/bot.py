```python
import os
import re
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# ==========================================
# CONFIG
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ==========================================
# START
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🤖 Link Ban Bot is online!\n\n"
        "🔗 Links: BLOCKED\n"
        "↪️ Forward messages: BLOCKED\n"
        "🚫 Spam: BLOCKED\n"
        "👑 Admins: ALLOWED"
    )


# ==========================================
# CHECK ADMIN
# ==========================================

async def is_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> bool:

    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat:
        return False

    if not message.from_user:
        return False

    try:

        member = await context.bot.get_chat_member(
            chat.id,
            message.from_user.id
        )

        return member.status in (
            "administrator",
            "creator",
        )

    except Exception as e:

        logger.warning(
            f"Admin check failed: {e}"
        )

        return False


# ==========================================
# LINK DETECTION
# ==========================================

def contains_link(text: str) -> bool:

    pattern = (
        r"(https?://\S+"
        r"|www\.\S+"
        r"|t\.me/\S+"
        r"|telegram\.me/\S+)"
    )

    return bool(
        re.search(
            pattern,
            text,
            re.IGNORECASE
        )
    )


# ==========================================
# SPAM DETECTION
# ==========================================

def contains_spam(text: str) -> bool:

    spam_patterns = [

        r"\bfree\s+money\b",

        r"\bfree\s+gift\b",

        r"\bclick\s+here\b",

        r"\bpromo\s+code\b",

        r"\bgiveaway\b",

        r"\bairdrop\b",

        r"\bdouble\s+your\s+money\b",

        r"\bmake\s+money\s+fast\b",

        r"\bwork\s+from\s+home\b",

        r"\bearn\s+money\b",

    ]

    for pattern in spam_patterns:

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            return True

    return False


# ==========================================
# MESSAGE MODERATION
# ==========================================

async def moderate_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat:
        return

    # Only groups
    if chat.type not in (
        "group",
        "supergroup",
    ):
        return

    # Admins are allowed
    if await is_admin(
        update,
        context
    ):
        return

    # ======================================
    # FORWARD MESSAGE
    # ======================================

    if message.forward_origin is not None:

        try:

            await message.delete()

            logger.info(
                "Forward message deleted."
            )

        except Exception as e:

            logger.warning(
                f"Could not delete forward: {e}"
            )

        return

    # ======================================
    # TEXT / CAPTION
    # ======================================

    text = (
        message.text
        or message.caption
        or ""
    )

    if not text:
        return

    # ======================================
    # LINK
    # ======================================

    if contains_link(text):

        try:

            await message.delete()

            logger.info(
                "Link message deleted."
            )

        except Exception as e:

            logger.warning(
                f"Could not delete link: {e}"
            )

        return

    # ======================================
    # SPAM
    # ======================================

    if contains_spam(text):

        try:

            await message.delete()

            logger.info(
                "Spam message deleted."
            )

        except Exception as e:

            logger.warning(
                f"Could not delete spam: {e}"
            )

        return


# ==========================================
# MAIN
# ==========================================

def main():

    if not BOT_TOKEN:

        print(
            "ERROR: BOT_TOKEN environment "
            "variable is not configured."
        )

        return

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Check all non-command messages
    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            moderate_message
        )
    )

    print(
        "================================"
    )

    print(
        "     IVR LINK BAN BOT"
    )

    print(
        "================================"
    )

    print(
        "🔗 Link protection: ON"
    )

    print(
        "↪️ Forward protection: ON"
    )

    print(
        "🚫 Spam protection: ON"
    )

    print(
        "👑 Admins: ALLOWED"
    )

    print(
        "🤖 Bot is running..."
    )

    print(
        "================================"
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    main()
```
