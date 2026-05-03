from telethon.tl.functions.channels import EditBannedRequest
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, UserNotParticipantError, UserAdminInvalidError
from .security import check_bot_admin_status, check_user_is_creator, check_user_admin_status
from .utils import log_moderation_action, logger
from .config import BAN_RIGHTS, UNBAN_RIGHTS

async def moderate_user(client, event, user, action, rights):
    try:
        user_name = f"@{user.username}" if user.username else user.first_name
        sender = await client.get_entity(event.sender_id)
        sender_name = f"@{sender.username}" if sender.username else sender.first_name
        if not await check_bot_admin_status(client, event.chat_id):
            await event.reply("❌ Bot is not an admin in this group or lacks necessary permissions.")
            log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
            return
        if await check_user_is_creator(client, event.chat_id, user.id):
            await event.reply("❌ Cannot moderate the group creator.")
            log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
            return
        if action in ["banned", "muted", "kick"] and await check_user_admin_status(client, event.chat_id, user.id):
            await event.reply("❌ Cannot moderate admins.")
            log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
            return
        me = await client.get_me()
        if user.id == me.id:
            await event.reply("❌ Bot cannot moderate itself.")
            log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
            return
        if action == "kick":
            await client(EditBannedRequest(event.chat_id, user.id, BAN_RIGHTS))
            await client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            await event.reply(f"✅ {user_name} has been kicked.")
        else:
            await client(EditBannedRequest(event.chat_id, user.id, rights))
            await event.reply(f"✅ {user_name} has been {action}.")
        log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, True)
        logger.info(f"Successfully {action} user {user.id} in chat {event.chat_id}")
    except ChatAdminRequiredError:
        await event.reply("❌ Bot needs admin privileges with ban/restrict permissions.")
        log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
    except UserNotParticipantError:
        await event.reply("❌ User is not in this group.")
        log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
    except UserAdminInvalidError:
        await event.reply("❌ Cannot moderate this admin.")
        log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
    except Exception as e:
        error_msg = str(e)
        if "participant ID is invalid" in error_msg:
            await event.reply("❌ User not found in this group.")
        elif "not an admin" in error_msg:
            await event.reply("❌ Bot lacks admin permissions or cannot moderate this user.")
        else:
            await event.reply(f"❌ {action.title()} failed: {error_msg[:50]}")
        log_moderation_action(event.sender_id, sender_name, action, user.id, user_name, event.chat_id, False)
        logger.error(f"Moderation error: {e}")
