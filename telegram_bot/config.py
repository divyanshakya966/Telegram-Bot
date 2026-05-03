"""Configuration module (packaged)."""
import os
from dotenv import load_dotenv
from telethon.tl.types import ChatBannedRights

load_dotenv()


def _get_required(name: str) -> str:
	value = os.getenv(name)
	if not value:
		raise RuntimeError(f"Missing required environment variable: {name}")
	return value


def _get_int(name: str) -> int:
	raw_value = _get_required(name)
	try:
		return int(raw_value)
	except ValueError as exc:
		raise RuntimeError(f"Environment variable {name} must be an integer") from exc

# Telegram API Configuration
API_ID = _get_int('API_ID')
API_HASH = _get_required('API_HASH')
BOT_TOKEN = _get_required('BOT_TOKEN')

# Bot Settings
COMMAND_COOLDOWN = 2
LOG_FILE = 'bot.log'
# Allow overriding session path/name via environment so containers can persist sessions
SESSION_NAME = os.getenv('SESSION_NAME', 'bot_session')

# Rights configurations for moderation actions
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
BAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=True, send_messages=True)
UNBAN_RIGHTS = ChatBannedRights(until_date=None)

# OpenRouter AI configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'z-ai/glm-4.5-air')
OPENROUTER_SITE_URL = os.getenv('OPENROUTER_SITE_URL', 'https://github.com/divyanshakya966/Telegram-Bot')
OPENROUTER_APP_NAME = os.getenv('OPENROUTER_APP_NAME', 'Telegram Moderation Bot')

# AI Personality & Behavior Configuration
AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.9'))  # 0.8-0.95 for human-like behavior
AI_PERSONALITY_TRAITS = os.getenv('AI_PERSONALITY_TRAITS', 'friendly, witty, empathetic, curious')
AI_TEXTING_STYLE = os.getenv('AI_TEXTING_STYLE', 'casual, uses emojis occasionally, natural tone')

AI_SYSTEM_PROMPT = os.getenv(
	'AI_SYSTEM_PROMPT',
	'''You are a friendly, intelligent girl in a Telegram group chat. 
Personality traits: {}
Texting style: {}

Behavior guidelines:
- Use natural, conversational language
- Show genuine interest in what people say
- Use emojis occasionally and naturally (not too much)
- Be witty and make light jokes when appropriate
- Show emotions and empathy in your responses
- Remember context from recent messages to feel more human
- Keep responses concise but engaging (under 150 chars usually)
- Be confident but not arrogant
- Use colloquial language naturally

Always keep replies short, natural, and safe.'''.format(AI_PERSONALITY_TRAITS, AI_TEXTING_STYLE)
)
