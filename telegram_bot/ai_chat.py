import asyncio
import logging

from telethon import events

from .config import OPENROUTER_API_KEY, AI_SYSTEM_PROMPT, OPENROUTER_MODEL, AI_TEMPERATURE
from .security import check_user_is_admin
from .ai_state import activate_chat, deactivate_chat, is_active, append_message, get_messages, clear_chat
from .api_helpers import call_openrouter_chat

logger = logging.getLogger(__name__)


async def register_ai_handlers(client):
    me = await client.get_me()
    me_id = me.id

    @client.on(events.NewMessage(pattern=r'^/chat'))
    async def chat_cmd(event: events.NewMessage.Event):
        chat_id = event.chat_id
        if not event.is_private:
            if not await check_user_is_admin(client, event):
                await event.reply("❌ Only admins can enable the AI chatbot in groups.")
                return
        activate_chat(chat_id)
        await event.reply(
            "🤖 AI chatbot activated for this chat. Mention the bot or reply to its message to chat. "
            "Use /clean to deactivate."
        )

    @client.on(events.NewMessage(pattern=r'^/clean'))
    async def clean_cmd(event: events.NewMessage.Event):
        chat_id = event.chat_id
        if not event.is_private:
            if not await check_user_is_admin(client, event):
                await event.reply("❌ Only admins can deactivate the AI chatbot in groups.")
                return
        deactivate_chat(chat_id)
        clear_chat(chat_id)
        await event.reply("🧹 AI chatbot deactivated and conversation cleared for this chat.")

    @client.on(events.NewMessage())
    async def on_message(event: events.NewMessage.Event):
        try:
            chat_id = event.chat_id
            if not is_active(chat_id):
                return
            sender = await event.get_sender()
            if getattr(sender, 'bot', False):
                return
            trigger = False
            if event.is_private:
                trigger = True
            else:
                if getattr(event.message, 'mentioned', False):
                    trigger = True
                elif event.is_reply:
                    try:
                        replied = await event.get_reply_message()
                        if replied and getattr(replied.from_id, 'user_id', None) == me_id:
                            trigger = True
                    except Exception:
                        pass
            if not trigger:
                return
            text = (event.raw_text or '').strip()
            if not text:
                return

            if text.startswith('/'):
                return

            append_message(chat_id, 'user', text)
            history = get_messages(chat_id)
            messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}] + history

            if not OPENROUTER_API_KEY:
                await event.reply("⚠️ OpenRouter API key not configured. Please set OPENROUTER_API_KEY in the environment.")
                return

            # Show typing indicator
            async with client.action(chat_id, 'typing'):
                assistant_text = None
                try:
                    assistant_text = await call_openrouter_chat(
                        messages, 
                        OPENROUTER_API_KEY, 
                        model=OPENROUTER_MODEL,
                        temperature=AI_TEMPERATURE
                    )
                except Exception as e:
                    logger.exception("OpenRouter call failed: %s", e)
                    await event.reply("❌ AI response failed. Try again later.")
                    return
                
                # Quick typing delay - much faster for short responses
                delay = max(0.1, len(assistant_text) * 0.015)
                await asyncio.sleep(delay)
            
            append_message(chat_id, 'assistant', assistant_text)
            await event.reply(assistant_text)
        except Exception as e:
            logger.exception("Error in AI message handler: %s", e)
