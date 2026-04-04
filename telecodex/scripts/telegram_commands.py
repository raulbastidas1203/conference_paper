#!/usr/bin/env python3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME = BASE_DIR / 'runtime'
INBOX = RUNTIME / 'inbox.jsonl'
EVENTS = RUNTIME / 'events.jsonl'
OUTBOX = RUNTIME / 'outbox.jsonl'
STATE = RUNTIME / 'command_state.json'


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'last_inbox_line': 0}


def save_state(state):
    STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def tail_jsonl(path: Path, n: int = 5):
    if not path.exists():
        return []
    lines = [x for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    out = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except Exception:
            out.append({'raw': line})
    return out


def append(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def handle_command(text: str):
    t = text.strip()
    if t == '/status':
        events = tail_jsonl(EVENTS, 3)
        summary = []
        for ev in events:
            et = ev.get('type', 'event')
            msg = ev.get('text', ev.get('raw', ''))
            summary.append(f'- {et}: {msg}')
        return 'Estado telecodex:\n' + ('\n'.join(summary) if summary else '- sin eventos recientes')
    if t == '/inbox':
        msgs = tail_jsonl(INBOX, 5)
        summary = []
        for m in msgs:
            summary.append(f"- {m.get('from','?')}: {m.get('text', m.get('raw',''))}")
        return 'Inbox reciente:\n' + ('\n'.join(summary) if summary else '- vacío')
    if t == '/last':
        events = tail_jsonl(EVENTS, 1)
        if not events:
            return 'No hay eventos recientes.'
        ev = events[-1]
        return f"Último evento: {ev.get('type','event')} - {ev.get('text', ev.get('raw',''))}"
    return None


def main():
    state = load_state()
    lines = INBOX.read_text(encoding='utf-8').splitlines() if INBOX.exists() else []
    new = lines[state.get('last_inbox_line', 0):]
    for line in new:
        line = line.strip()
        if not line:
            state['last_inbox_line'] += 1
            continue
        try:
            item = json.loads(line)
        except Exception:
            state['last_inbox_line'] += 1
            continue
        text = item.get('text', '').strip()
        reply = handle_command(text)
        if reply:
            append(OUTBOX, {
                'kind': 'reply',
                'chat_id': item.get('chat_id'),
                'text': reply,
            })
        state['last_inbox_line'] += 1
    save_state(state)


if __name__ == '__main__':
    main()
