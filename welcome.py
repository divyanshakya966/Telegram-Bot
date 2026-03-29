import random
import asyncio
from telethon import events
from telethon.tl.types import (
    MessageEntityMention, MessageEntityMentionName,
    UserStatusOnline, UserStatusOffline, UserStatusRecently,
    UserStatusLastWeek, UserStatusLastMonth, UserStatusEmpty
)
from datetime import datetime, timezone, timedelta
from security import check_user_is_admin
from utils import logger

# Track recently welcomed and farewelled users to prevent duplicates
recently_welcomed = set()
recently_farewelled = set()

def format_user_status(status):
    """
    Converts a Telegram UserStatus object to a human-readable string.
    """
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

async def send_fancy_welcome(client, chat, target_user, reply_to=None):
    """Send the fancy welcome message with image and formatted text"""
    greetings = [
        "🌸 A warm welcome to you!",
        "✨ We're glad to have you here!",
        "🥳 Let's make some memories together!",
        "💫 Hope you enjoy your stay!",
        "🔥 Welcome aboard!"
    ]

    greeting_text = random.choice(greetings)
    group_name = chat.title if hasattr(chat, 'title') and chat.title else "this group"
    name_clickable = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"
    username_display = f"@{target_user.username}" if target_user.username else "none"
    user_id_plain = f"<code>{target_user.id}</code>"

    caption = (
        f"""<blockquote>{greeting_text}
<b>Welcome to</b>
<b>{group_name}</b></blockquote>"""
        "▰▱▱▱▱▱▱▱▱▱▱▱▱▱▰\n"
        f"""<blockquote>➻ <b>Name</b> ➝ {name_clickable}
➻ <b>ID</b> ➝ {user_id_plain}
➻ <b>Username</b> ➝ {username_display}</blockquote>"""
        "❅─────✧❅✦❅✧─────❅\n"
        """<blockquote>★ MAKE NEW FRIENDS
★ NSFW/PM, DM/PROMOTION = BAN
★ FLIRT IN LIMITS
★ GIVE RESPECT = TAKE RESPECT
★ FOR QUERIES, TYPE @admins</blockquote>"""
        "▰▱▱▱▱▱▱▱▱▱▱▱▱▱▰"
    )

    # Update this path to your welcome image
    file_path = r"video_2026-03-29_14-12-49.mp4"

    try:
        await client.send_file(
            chat, file_path, caption=caption,
            reply_to=reply_to, parse_mode="html",
            supports_streaming=True,
            force_document=False
        )
    except Exception as e:
        # If video fails, send text only
        await client.send_message(chat, caption, parse_mode="html", reply_to=reply_to)
        logger.error(f"Welcome video failed: {e}")

async def send_fancy_goodbye(client, chat, target_user):
    """Send the goodbye message when user leaves"""
    name_clickable = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"
    
    goodbye_message = (
        f"Goodbye, {name_clickable}! 👋\n"
        "We'll miss having you here! Thanks for being part of the community. "
        "Wishing you all the best! Feel free to come back anytime. 😊🌟"
    )
    
    try:
        await client.send_message(chat, goodbye_message, parse_mode="html")
        logger.info(f"Sent goodbye message for user {target_user.id}")
    except Exception as e:
        logger.error(f"Goodbye message failed: {e}")

async def remove_from_set(s, key, delay):
    """Remove key from set after delay"""
    await asyncio.sleep(delay)
    s.discard(key)

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

async def register_welcome_handler(client):
    # Ignore historical service events from before this process started.
    bot_started_at = datetime.now(timezone.utc)
    startup_grace_until = bot_started_at + timedelta(seconds=20)

    @client.on(events.ChatAction)
    async def auto_welcome_goodbye_handler(event):
        """Handle both welcome and goodbye events"""
        try:
            now_utc = datetime.now(timezone.utc)
            action_message = getattr(event, 'action_message', None)
            action_date = getattr(action_message, 'date', None)
            if action_date is not None:
                if action_date.tzinfo is None:
                    action_date = action_date.replace(tzinfo=timezone.utc)
                if action_date < bot_started_at - timedelta(seconds=5):
                    logger.info("Skipping stale chat action event from before startup")
                    return

            chat = await event.get_chat()

            # Welcome logic
            if event.user_joined or event.user_added:
                if event.user:
                    target_user = await event.get_user()
                    key = f"welcome_{target_user.id}_{chat.id}"
                    if key not in recently_welcomed:
                        recently_welcomed.add(key)
                        await send_fancy_welcome(client, chat, target_user)
                        logger.info(f"Auto-welcomed user {target_user.id} to {chat.id}")
                        asyncio.create_task(remove_from_set(recently_welcomed, key, 30))
                    else:
                        logger.info(f"Skipped duplicate welcome for user {target_user.id}")
                
                elif event.users:
                    users = await event.get_users()
                    for target_user in users:
                        key = f"welcome_{target_user.id}_{chat.id}"
                        if key not in recently_welcomed:
                            recently_welcomed.add(key)
                            await send_fancy_welcome(client, chat, target_user)
                            logger.info(f"Auto-welcomed user {target_user.id} to {chat.id}")
                            asyncio.create_task(remove_from_set(recently_welcomed, key, 30))
                            await asyncio.sleep(1)

            # Goodbye logic
            if event.user_left or event.user_kicked:
                if now_utc < startup_grace_until:
                    logger.info("Skipping leave/kick chat action during startup grace period")
                    return

                if event.user:
                    target_user = await event.get_user()
                    key = f"goodbye_{target_user.id}_{chat.id}"
                    if key not in recently_farewelled:
                        recently_farewelled.add(key)
                        await send_fancy_goodbye(client, chat, target_user)
                        logger.info(f"Said goodbye to user {target_user.id} from {chat.id}")
                        asyncio.create_task(remove_from_set(recently_farewelled, key, 30))
                    else:
                        logger.info(f"Skipped duplicate goodbye for user {target_user.id}")
                
                elif event.users:
                    users = await event.get_users()
                    for target_user in users:
                        key = f"goodbye_{target_user.id}_{chat.id}"
                        if key not in recently_farewelled:
                            recently_farewelled.add(key)
                            await send_fancy_goodbye(client, chat, target_user)
                            logger.info(f"Said goodbye to user {target_user.id} from {chat.id}")
                            asyncio.create_task(remove_from_set(recently_farewelled, key, 30))
                            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Auto welcome/goodbye error: {e}")

    # Manual welcome handler
    @client.on(events.NewMessage(pattern=r'^/welcome(?:\s+(.*))?$'))
    async def manual_welcome(event):
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can use this command.")
            return

        chat = await event.get_chat()
        target_user = None

        # Method 1: Reply to user's message
        if event.is_reply:
            replied_msg = await event.get_reply_message()
            target_user = await client.get_entity(replied_msg.sender_id)

        # Method 2: Username mention in command
        elif event.pattern_match.group(1):
            mention_text = event.pattern_match.group(1).strip()
            if mention_text.startswith('@'):
                try:
                    target_user = await client.get_entity(mention_text)
                except Exception:
                    pass

        # Method 3: Message entity mention
        elif event.message.entities:
            for entity in event.message.entities:
                try:
                    if isinstance(entity, MessageEntityMention):
                        username = event.message.raw_text[entity.offset:entity.offset + entity.length]
                        target_user = await client.get_entity(username)
                    elif isinstance(entity, MessageEntityMentionName):
                        target_user = await client.get_entity(entity.user_id)
                    if target_user:
                        break
                except Exception:
                    continue

        if not target_user:
            usage_msg = (
                "**🔸 Welcome Command Usage:**\n\n"
                "**Method 1:** `/welcome @username`\n"
                "**Method 2:** Reply to user's message with `/welcome`\n"
            )
            await event.reply(usage_msg)
            return

        await send_fancy_welcome(client, chat, target_user, event.reply_to_msg_id)

    # Manual goodbye handler
    @client.on(events.NewMessage(pattern=r'^/goodbye(?:\s+(.*))?$'))
    async def manual_goodbye(event):
        """Remove user from group and send goodbye message"""
        if not await check_user_is_admin(client, event):
            await event.reply("❌ Only admins can use this command.")
            return

        chat = await event.get_chat()
        target_user = None

        # Method 1: Reply to user's message
        if event.is_reply:
            replied_msg = await event.get_reply_message()
            target_user = await client.get_entity(replied_msg.sender_id)

        # Method 2: Username mention in command
        elif event.pattern_match.group(1):
            mention_text = event.pattern_match.group(1).strip()
            if mention_text.startswith('@'):
                try:
                    target_user = await client.get_entity(mention_text)
                except Exception:
                    pass

        # Method 3: Message entity mention
        elif event.message.entities:
            for entity in event.message.entities:
                try:
                    if isinstance(entity, MessageEntityMention):
                        username = event.message.raw_text[entity.offset:entity.offset + entity.length]
                        target_user = await client.get_entity(username)
                    elif isinstance(entity, MessageEntityMentionName):
                        target_user = await client.get_entity(entity.user_id)
                    if target_user:
                        break
                except Exception:
                    continue

        if not target_user:
            usage_msg = (
                "**🔸 Goodbye Command Usage:**\n\n"
                "**Method 1:** `/goodbye @username`\n"
                "**Method 2:** Reply to user's message with `/goodbye`\n\n"
                "⚠️ **Warning:** This will remove the user from the group!"
            )
            await event.reply(usage_msg)
            return

        # Check if trying to remove an admin
        try:
            user_permissions = await client.get_permissions(chat, target_user)
            if user_permissions.is_admin:
                await event.reply("❌ Cannot remove an admin from the group!")
                return
        except Exception:
            pass

        # Check if trying to remove yourself
        if target_user.id == event.sender_id:
            await event.reply("❌ You cannot remove yourself using this command!")
            return

        try:
            # Remove the user from the group
            # The automatic ChatAction handler will detect this kick and send the goodbye message
            await client.kick_participant(chat, target_user)
            
            # Just confirm action to the admin - let automatic handler send goodbye message
            await event.reply(f"✅ Successfully removed {target_user.first_name} from the group.")
            
            logger.info(f"Admin {event.sender_id} removed user {target_user.id} from {chat.id}")
            
        except Exception as e:
            await event.reply(f"❌ Failed to remove user: {str(e)}")
            logger.error(f"Failed to remove user {target_user.id}: {e}")
