from telethon import events
from .security import check_rate_limit, check_user_is_admin, check_bot_admin_status
from .user_mgmt import get_user_from_event
from .moderation import moderate_user
from .utils import get_recent_logs, format_log_text, logger
from .config import BAN_RIGHTS, MUTE_RIGHTS, UNBAN_RIGHTS
from .welcome import register_welcome_handler
from .userinfo import register_userinfo_handler
from .ai_chat import register_ai_handlers

async def register_handlers(client):
    """Register all command handlers"""

    @client.on(events.NewMessage(pattern=r'^/ban'))
    async def ban_cmd(event):
        if not check_rate_limit(event.sender_id):
            await event.reply("⏱️ Please wait before using another command.")
            return
        
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can use this command.")
            return
        
        user = await get_user_from_event(client, event)
        if user:
            await moderate_user(client, event, user, "banned", BAN_RIGHTS)

    @client.on(events.NewMessage(pattern=r'^/unban'))
    async def unban_cmd(event):
        if not check_rate_limit(event.sender_id):
            await event.reply("⏱️ Please wait before using another command.")
            return
        
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can use this command.")
            return
        
        user = await get_user_from_event(client, event)
        if user:
            await moderate_user(client, event, user, "unbanned", UNBAN_RIGHTS)

    @client.on(events.NewMessage(pattern=r'^/mute'))
    async def mute_cmd(event):
        if not check_rate_limit(event.sender_id):
            await event.reply("⏱️ Please wait before using another command.")
            return
        
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can use this command.")
            return
        
        user = await get_user_from_event(client, event)
        if user:
            await moderate_user(client, event, user, "muted", MUTE_RIGHTS)

    @client.on(events.NewMessage(pattern=r'^/unmute'))
    async def unmute_cmd(event):
        if not check_rate_limit(event.sender_id):
            await event.reply("⏱️ Please wait before using another command.")
            return
        
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can use this command.")
            return
        
        user = await get_user_from_event(client, event)
        if user:
            await moderate_user(client, event, user, "unmuted", UNBAN_RIGHTS)

    @client.on(events.NewMessage(pattern=r'^/kick'))
    async def kick_cmd(event):
        if not check_rate_limit(event.sender_id):
            await event.reply("⏱️ Please wait before using another command.")
            return
        
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can use this command.")
            return
        
        user = await get_user_from_event(client, event)
        if user:
            await moderate_user(client, event, user, "kick", None)

    @client.on(events.NewMessage(pattern=r'^/help'))
    async def help_cmd(event):
        with open("text_files/help_text.txt", encoding="utf-8") as help_text:
            await event.reply(help_text.read())

    @client.on(events.NewMessage(pattern=r'^/start'))
    async def help_cmd(event):
        with open("text_files/start_text.txt", encoding="utf-8") as start_text:
            await event.reply(start_text.read())

    @client.on(events.NewMessage(pattern=r'^/status'))
    async def status_cmd(event):
        try:
            me = await client.get_me()
            is_admin = await check_bot_admin_status(client, event.chat_id)
            user_is_admin = await check_user_is_admin(client, event)
            with open("text_files/status_text.txt", "r", encoding="utf-8") as f:
                text = f.read()
            status_text = eval(f'f"""{text}"""')
            await event.reply(status_text)
        except Exception as e:
            await event.reply(f"Status check failed: {e}")

    @client.on(events.NewMessage(pattern=r'^/logs'))
    async def logs_cmd(event):
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can view logs.")
            return
        
        logs = get_recent_logs()
        log_text = format_log_text(logs)
        await event.reply(log_text)

    await register_welcome_handler(client)
    await register_userinfo_handler(client)
    # Register AI chat handlers (/chat and /clean) and message listener
    await register_ai_handlers(client)
