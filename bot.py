"""
Telegram Moderation Bot - Main Entry Point

This is the main entry point for the Telegram moderation bot.
It initializes the Telethon client, registers all command handlers,
and starts the bot to listen for events.

Author: Divyansh Shakya
Repository: https://github.com/divyanshakya966/Telegram-Bot
"""

import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_NAME
from commands import register_handlers
from utils import logger

async def main():
    """
    Initialize and run the Telegram bot.
    
    This function:
    1. Creates a Telethon client with API credentials
    2. Registers all command and event handlers
    3. Starts the bot using the bot token
    4. Keeps the bot running until manually stopped
    
    Raises:
        Exception: If bot initialization or startup fails
    """
    try:
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

        await client.start(bot_token=BOT_TOKEN)

        # Register handlers only after the client is connected/authenticated.
        await register_handlers(client)
        
        print("✅ Bot started successfully!")
        print("💡 Use /status in your group to check bot permissions")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Bot error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
