Fly.io deploy guide for this Telegram bot

Prerequisites
- Install `flyctl`: https://fly.io/docs/hands-on/install-flyctl/
- Have a Fly account and be logged in: `flyctl auth login`

Quick setup
1. Create app and volume

```bash
flyctl apps create my-telegram-bot
flyctl volumes create bot-data --size 1
```

2. Set required secrets (replace placeholders)

```bash
flyctl secrets set API_ID=12345 API_HASH="xxx" BOT_TOKEN="xxx"
# optional
flyctl secrets set OPENROUTER_API_KEY="xxx"
```

3. Tell the app to save the Telethon session file on the persistent volume

```bash
flyctl secrets set SESSION_NAME="/data/bot_session"
```

4. Deploy

```bash
flyctl deploy
```

Notes & tips
- `fly.toml` in this repo includes a mounts section that expects a volume named `bot-data` mounted at `/data`.
- The app will run `python run.py` (see `Dockerfile`). `run.py` runs `telegram_bot.main()` which uses Telethon.
- If you prefer to set the session as a string, you can use Telethon `StringSession` and store it with `flyctl secrets set`, but mounting a small volume is simpler.
- To view logs:

```bash
flyctl logs -a my-telegram-bot
```

Useful commands

```bash
# scale to 1 VM
flyctl scale count 1 -a my-telegram-bot

# run a one-off command inside the app (helpful for debugging)
flyctl ssh console -a my-telegram-bot
```
