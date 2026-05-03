from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import User
from telethon.errors.rpcerrorlist import UsernameInvalidError, PeerIdInvalidError, UserNotParticipantError
from .utils import logger

async def validate_participant(client, chat_id, user_id):
    try:
        await client(GetParticipantRequest(
            channel=chat_id,
            participant=user_id
        ))
        return True
    except UserNotParticipantError:
        return False
    except Exception as e:
        logger.error(f"Error validating participant: {e}")
        return False

async def get_user_from_event(client, event):
    try:
        message_text = event.raw_text.strip()
        parts = message_text.split()
        if len(parts) > 1:
            username_part = parts[1].strip()
            if username_part.startswith('@'):
                username_part = username_part[1:]
            try:
                if username_part.isdigit():
                    user = await client.get_entity(int(username_part))
                else:
                    user = await client.get_entity(username_part)
                if not isinstance(user, User):
                    await event.reply("❌ That's not a user account.")
                    return None
                if not await validate_participant(client, event.chat_id, user.id):
                    await event.reply("❌ User is not a member of this group.")
                    return None
                return user
            except (UsernameInvalidError, ValueError, PeerIdInvalidError):
                await event.reply(f"❌ User not found: {username_part}")
                return None
            except Exception as e:
                await event.reply(f"❌ Error finding user: {str(e)[:50]}")
                return None
        elif event.is_reply:
            try:
                reply = await event.get_reply_message()
                if not reply or not reply.sender_id:
                    await event.reply("❌ Could not get user from replied message.")
                    return None
                user = await client.get_entity(reply.sender_id)
                if not isinstance(user, User):
                    await event.reply("❌ Replied message is not from a user.")
                    return None
                if not await validate_participant(client, event.chat_id, user.id):
                    await event.reply("❌ User is not a member of this group.")
                    return None
                return user
            except Exception as e:
                await event.reply("❌ Error getting user from reply.")
                logger.error(f"Reply error: {e}")
                return None
        else:
            await event.reply("❌ Please reply to a user or use @username")
            return None
    except Exception as e:
        logger.error(f"Error in get_user_from_event: {e}")
        await event.reply("❌ Error processing command.")
        return None
