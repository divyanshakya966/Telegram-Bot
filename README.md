# Telegram Moderation Bot

A modular Telegram bot built with Telethon. It supports moderation, welcome/goodbye automation, user info, and an AI chatbot powered by OpenRouter.

## Features

- Ban, unban, mute, unmute, and kick users
- Automatic and manual welcome/goodbye messages
- User info command
- Logs for moderation actions
- AI chatbot with `/chat` and `/clean`

## Project Structure

```text
Telegram-Bot/
├── run.py
├── requirements.txt
├── .env.example
├── telegram_bot/
│   ├── __init__.py
│   ├── bot.py
│   ├── commands.py
│   ├── config.py
│   ├── security.py
│   ├── moderation.py
│   ├── user_mgmt.py
│   ├── welcome.py
│   ├── userinfo.py
│   ├── utils.py
│   ├── ai_chat.py
│   ├── ai_state.py
│   ├── api_helpers.py
│   └── media/
└── text_files/
```

## Environment Variables

Create a `.env` file from `.env.example` and fill in:

```env
API_ID='12345678'
API_HASH='your_api_hash'
BOT_TOKEN='your_bot_token'
OPENROUTER_API_KEY='your_openrouter_key'
OPENROUTER_MODEL='cognitivecomputations/dolphin-mistral-24b-venice-edition:free'
OPENROUTER_SITE_URL='https://your-app.example.com'
OPENROUTER_APP_NAME='Telegram Moderation Bot'
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the bot:

```bash
python run.py
```

## OpenRouter AI Setup

The `/chat` command activates the AI chatbot per chat. When active, the bot replies when:

- someone mentions the bot username, or
- someone replies to one of the bot's messages.

The AI client sends requests to:

```text
https://openrouter.ai/api/v1/chat/completions
```

Current model default:

```text
cognitivecomputations/dolphin-mistral-24b-venice-edition:free
```

To change the model, update `OPENROUTER_MODEL` in `.env`.

## Telegram Setup

1. Create a bot with [@BotFather](https://t.me/BotFather).
2. Get your `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org/apps).
3. Add the bot to your group.
4. Promote it to admin if you want moderation and welcome/goodbye features.
5. For AI replies, set `OPENROUTER_API_KEY` in `.env`.

## Deployment Steps for Backend Hosting

Deploy on PaaS platforms like Render or JustRunMyApp. Set these environment variables:

- `API_ID`
- `API_HASH`
- `BOT_TOKEN`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `OPENROUTER_SITE_URL`
- `OPENROUTER_APP_NAME`

Start command for your platform:

```bash
python run.py
```

## Commands

- `/ban`, `/unban`, `/mute`, `/unmute`, `/kick`
- `/help`, `/start`, `/status`, `/logs`
- `/welcome`, `/goodbye`, `/uinfo`
- `/chat` to enable AI replies in a chat
- `/clean` to deactivate AI replies and clear the session

## Notes

- The bot stores AI session state in `ai_state.json`.
- The welcome media is stored in `telegram_bot/media/`.
- The bot uses a modular package layout under `telegram_bot/`.
