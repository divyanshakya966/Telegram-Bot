"""Entrypoint that runs the packaged telegram bot."""
import asyncio
from telegram_bot import main

if __name__ == '__main__':
    asyncio.run(main())
