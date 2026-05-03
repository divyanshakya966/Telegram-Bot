"""Package bot entry: initializes Telethon client and starts the bot."""
import asyncio
from telethon import TelegramClient
from .config import API_ID, API_HASH, BOT_TOKEN, SESSION_NAME
from .commands import register_handlers
from .utils import logger


async def main():
    try:
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

        await client.start(bot_token=BOT_TOKEN)

        await register_handlers(client)

        print("✅ Bot started successfully!")
        print("💡 Use /status in your group to check bot permissions")

        await client.run_until_disconnected()

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Bot error: {e}")
