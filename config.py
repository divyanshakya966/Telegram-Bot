"""
Configuration Module for Telegram Moderation Bot

This module loads environment variables and defines bot configuration settings
including API credentials, command cooldown, and permission rights for user moderation.

Environment variables should be set in a .env file:
- API_ID: Your Telegram API ID from https://my.telegram.org/apps
- API_HASH: Your Telegram API Hash from https://my.telegram.org/apps
- BOT_TOKEN: Your bot token from @BotFather

Author: Divyansh Shakya
"""

import os
from dotenv import load_dotenv
from telethon.tl.types import ChatBannedRights

load_dotenv()

# Telegram API Configuration
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Bot Settings
COMMAND_COOLDOWN = 2
LOG_FILE = 'bot.log'
SESSION_NAME = 'bot_session'

# Rights configurations for moderation actions
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
BAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=True, send_messages=True)
UNBAN_RIGHTS = ChatBannedRights(until_date=None)
