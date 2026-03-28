from telethon import events
from telethon.tl.types import (
    UserStatusOnline, UserStatusOffline, UserStatusRecently,
    UserStatusLastWeek, UserStatusLastMonth, UserStatusEmpty
)
from datetime import datetime
from utils import logger

def format_user_status(status):
    """Converts a Telegram UserStatus object to a human-readable string."""
    if isinstance(status, UserStatusOnline):
        return "🟢 Online"
    
    elif isinstance(status, UserStatusOffline):
        if hasattr(status, 'was_online'):
            try:
                last_online = datetime.fromtimestamp(status.was_online)
                return f"🔴 Last seen {last_online.strftime('%Y-%m-%d %H:%M:%S')}"
            except:
                return "🔴 Offline"
        return "🔴 Offline"
    
    elif isinstance(status, UserStatusRecently):
        if hasattr(status, 'by_me') and status.by_me:
            return "🟡 Last seen recently (Premium required to see exact time)"
        return "🟡 Last seen recently"
    
    elif isinstance(status, UserStatusLastWeek):
        if hasattr(status, 'by_me') and status.by_me:
            return "🟠 Last seen within a week (Premium required to see exact time)"
        return "🟠 Last seen within a week"
    
    elif isinstance(status, UserStatusLastMonth):
        if hasattr(status, 'by_me') and status.by_me:
            return "🟤 Last seen within a month (Premium required to see exact time)"
        return "🟤 Last seen within a month"
    
    elif isinstance(status, UserStatusEmpty):
        return "⚫ Status not set"
    
    else:
        return f"❓ Unknown status: {type(status).__name__}"

async def register_userinfo_handler(client):
    @client.on(events.NewMessage(pattern=r'^/uinfo(?:\s+(@?\w+))?'))
    async def userinfo_handler(event):
        args = event.pattern_match.group(1)
        target_user = None
        try:
            if args:
                arg = args.strip()
                if arg.startswith('@'):
                    arg = arg[1:]
                target_user = await client.get_entity(arg)
            elif event.is_reply:
                replied = await event.get_reply_message()
                target_user = await client.get_entity(replied.sender_id)
            else:
                await event.reply("❌ Please reply to a user or provide a username with /uinfo @username")
                return
        except Exception as e:
            await event.reply(f"❌ Could not fetch user info: {str(e)}")
            logger.error(f"Userinfo fetch error: {e}")
            return

        entity = target_user
        text = "<b>📊 User Information:</b>\n\n"
        text += f"🆔 <b>ID:</b> <code>{entity.id}</code>\n"
        text += f"👤 <b>Name:</b> {entity.first_name or ''} {entity.last_name or ''}\n"
        text += f"📛 <b>Username:</b> @{entity.username or 'None'}\n"
        text += f"📞 <b>Phone:</b> {entity.phone or 'None'}\n"
        text += f"🤖 <b>Bot:</b> {'Yes' if entity.bot else 'No'}\n"
        text += f"✅ <b>Verified:</b> {'Yes' if getattr(entity, 'verified', False) else 'No'}\n"
        text += f"⚠️ <b>Scam:</b> {'Yes' if getattr(entity, 'scam', False) else 'No'}\n"
        text += f"🚫 <b>Restricted:</b> {'Yes' if getattr(entity, 'restricted', False) else 'No'}\n"
        text += f"❌ <b>Deleted:</b> {'Yes' if getattr(entity, 'deleted', False) else 'No'}\n"
        text += f"⭐ <b>Premium:</b> {'Yes' if getattr(entity, 'premium', False) else 'No'}\n"
        
        # Additional info if available
        if hasattr(entity, 'status'):
            text += f"<b>Status:</b> {format_user_status(entity.status)}\n"
        
        if hasattr(entity, 'restriction_reason') and entity.restriction_reason:
            text += f"🔒 <b>Restriction:</b> {entity.restriction_reason}\n"

        await event.reply(text, parse_mode='html')
