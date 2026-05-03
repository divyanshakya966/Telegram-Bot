import json
import threading
from pathlib import Path
from typing import List, Dict

_LOCK = threading.Lock()
_STATE_FILE = Path('ai_state.json')

def _load_state() -> Dict:
    if not _STATE_FILE.exists():
        return {'active': {}, 'conversations': {}, 'emotional_memory': {}}
    try:
        return json.loads(_STATE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {'active': {}, 'conversations': {}, 'emotional_memory': {}}

def _save_state(state: Dict) -> None:
    with _LOCK:
        _STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')

def activate_chat(chat_id: int) -> None:
    state = _load_state()
    state['active'][str(chat_id)] = True
    state['conversations'].setdefault(str(chat_id), [])
    _save_state(state)

def deactivate_chat(chat_id: int) -> None:
    state = _load_state()
    state['active'].pop(str(chat_id), None)
    state['conversations'].pop(str(chat_id), None)
    _save_state(state)

def is_active(chat_id: int) -> bool:
    state = _load_state()
    return bool(state.get('active', {}).get(str(chat_id), False))

def append_message(chat_id: int, role: str, content: str, max_turns: int = 20) -> None:
    state = _load_state()
    conv = state.setdefault('conversations', {}).setdefault(str(chat_id), [])
    conv.append({'role': role, 'content': content})
    if len(conv) > max_turns:
        del conv[0: len(conv) - max_turns]
    state['conversations'][str(chat_id)] = conv
    _save_state(state)

def get_messages(chat_id: int) -> List[Dict[str, str]]:
    state = _load_state()
    return state.get('conversations', {}).get(str(chat_id), [])

def clear_chat(chat_id: int) -> None:
    state = _load_state()
    state.setdefault('conversations', {})[str(chat_id)] = []
    _save_state(state)

def update_emotional_memory(chat_id: int, emotion: str, context: str) -> None:
    """Track emotional memory to remember user interactions and emotional context."""
    state = _load_state()
    memory = state.setdefault('emotional_memory', {}).setdefault(str(chat_id), {
        'mood': 'neutral',
        'recent_topics': [],
        'user_preferences': []
    })
    memory['mood'] = emotion
    if context not in memory['recent_topics']:
        memory['recent_topics'].append(context)
    if len(memory['recent_topics']) > 10:
        memory['recent_topics'].pop(0)
    state['emotional_memory'][str(chat_id)] = memory
    _save_state(state)

def get_emotional_memory(chat_id: int) -> Dict:
    """Retrieve emotional memory to add context to responses."""
    state = _load_state()
    return state.get('emotional_memory', {}).get(str(chat_id), {
        'mood': 'neutral',
        'recent_topics': [],
        'user_preferences': []
    })
