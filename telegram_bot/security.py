import time
from collections import defaultdict
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from .utils import logger
from .config import COMMAND_COOLDOWN

# Rate limiting storage: tracks last command time for each user
user_last_command = defaultdict(float)

def check_rate_limit(user_id):
    current_time = time.time()
    last_command_time = user_last_command[user_id]
    if current_time - last_command_time < COMMAND_COOLDOWN:
        return False
    user_last_command[user_id] = current_time
    return True

async def check_user_is_admin(client, event):
    try:
        sender_id = event.sender_id
        participant = await client(GetParticipantRequest(
            channel=event.chat_id,
            participant=sender_id
        ))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking sender admin status: {e}")
        return False

async def check_user_is_creator(client, chat_id, user_id):
    try:
        participant = await client(GetParticipantRequest(
            channel=chat_id,
            participant=user_id
        ))
        return isinstance(participant.participant, ChannelParticipantCreator)
    except Exception as e:
        logger.error(f"Error checking creator status: {e}")
        return False

async def check_bot_admin_status(client, chat_id):
    try:
        me = await client.get_me()
        participant = await client(GetParticipantRequest(
            channel=chat_id,
            participant=me.id
        ))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking bot admin status: {e}")
        return False

async def check_user_admin_status(client, chat_id, user_id):
    try:
        participant = await client(GetParticipantRequest(
            channel=chat_id,
            participant=user_id
        ))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking user admin status: {e}")
        return False
