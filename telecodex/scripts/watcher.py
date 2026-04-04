#!/usr/bin/env python3
import argparse
import json
import os
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME_DIR = BASE_DIR / 'runtime'
EVENTS_PATH = RUNTIME_DIR / 'events.jsonl'
INBOX_PATH = RUNTIME_DIR / 'inbox.jsonl'
STATE_PATH = RUNTIME_DIR / 'state.json'
CONFIG_PATH = BASE_DIR / 'config' / 'telegram.settings.json'

DEFAULT_STATE = {
    'last_event_line': 0,
    'last_update_id': None,
    'last_notified_text': None,
}


def ensure_runtime():
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    for p in (EVENTS_PATH, INBOX_PATH):
        if not p.exists():
            p.write_text('')
    if not STATE_PATH.exists():
        STATE_PATH.write_text(json.dumps(DEFAULT_STATE, indent=2))


def load_state():
    ensure_runtime()
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return dict(DEFAULT_STATE)


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def load_dotenv():
    env_path = BASE_DIR / '.env'
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v


def load_config():
    load_dotenv()
    data = {}
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
        except Exception:
            data = {}
    token = os.getenv('CODEX_TELEGRAM_BOT_TOKEN') or os.getenv('TELECODEX_BOT_TOKEN') or data.get('botToken')
    if token in (None, '', 'SET_VIA_ENV_OR_LOCAL_ONLY'):
        token = None
    chat_id = os.getenv('CODEX_TELEGRAM_CHAT_ID') or os.getenv('TELECODEX_CHAT_ID') or data.get('chatId')
    if chat_id in (None, '', 'SET_REAL_CHAT_ID'):
        chat_id = None
    return token, str(chat_id) if chat_id else None


def tg_api(token, method, **params):
    url = f'https://api.telegram.org/bot{token}/{method}'
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def send_message(token, chat_id, text):
    if not token or not chat_id:
        return None
    try:
        return tg_api(token, 'sendMessage', chat_id=chat_id, text=text)
    except Exception:
        return None


def append_jsonl(path: Path, obj: dict):
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def summarize_event(ev: dict):
    et = ev.get('type', 'event')
    txt = ev.get('text') or ev.get('message') or ''
    if et == 'progress':
        return f"🛠️ {txt}"
    if et == 'waiting':
        return f"⏳ {txt}"
    if et == 'done':
        return f"✅ {txt}"
    if et == 'error':
        return f"❌ {txt}"
    return f"ℹ️ {txt or json.dumps(ev, ensure_ascii=False)[:250]}"


def process_events(state, token, chat_id):
    ensure_runtime()
    lines = EVENTS_PATH.read_text(encoding='utf-8').splitlines()
    start = state.get('last_event_line', 0)
    new_lines = lines[start:]
    sent = 0
    for line in new_lines:
        line = line.strip()
        if not line:
            state['last_event_line'] = state.get('last_event_line', 0) + 1
            continue
        try:
            ev = json.loads(line)
        except Exception:
            ev = {'type': 'event', 'text': line}
        text = summarize_event(ev)
        if text != state.get('last_notified_text'):
            send_message(token, chat_id, text)
            state['last_notified_text'] = text
            sent += 1
        state['last_event_line'] = state.get('last_event_line', 0) + 1
    return sent


def process_updates(state, token, chat_id):
    if not token:
        return 0
    params = {}
    if state.get('last_update_id') is not None:
        params['offset'] = int(state['last_update_id']) + 1
    data = tg_api(token, 'getUpdates', **params)
    updates = data.get('result', [])
    ingested = 0
    for upd in updates:
        state['last_update_id'] = upd.get('update_id', state.get('last_update_id'))
        msg = upd.get('message') or {}
        chat = msg.get('chat') or {}
        if chat_id and str(chat.get('id')) != str(chat_id):
            continue
        text = msg.get('text')
        if not text:
            continue
        append_jsonl(INBOX_PATH, {
            'ts': int(time.time()),
            'source': 'telegram',
            'chat_id': str(chat.get('id')),
            'from': msg.get('from', {}).get('username') or msg.get('from', {}).get('first_name'),
            'message_id': msg.get('message_id'),
            'text': text,
        })
        ingested += 1
    return ingested


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--interval', type=float, default=3.0)
    args = parser.parse_args()

    token, chat_id = load_config()
    state = load_state()

    while True:
        process_events(state, token, chat_id)
        process_updates(state, token, chat_id)
        save_state(state)
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
