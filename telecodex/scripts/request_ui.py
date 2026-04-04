#!/usr/bin/env python3
import json
from pathlib import Path

RUNTIME = Path('/home/raul/CLAUDE/openclaw/telecodex/runtime')
PENDING_UI = RUNTIME / 'pending_ui_requests.json'
OUTBOX = RUNTIME / 'outbox.jsonl'


def append(obj):
    OUTBOX.parent.mkdir(parents=True, exist_ok=True)
    with OUTBOX.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def save_pending(data):
    PENDING_UI.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def load_pending():
    if PENDING_UI.exists():
        try:
            return json.loads(PENDING_UI.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def emit_request(chat_id: str, alias: str, raw_text: str):
    try:
        payload = json.loads(raw_text)
    except Exception:
        append({'kind': 'reply', 'chat_id': chat_id, 'text': f'{alias} te está pidiendo respuesta, pero no pude parsear las opciones.\n\n{raw_text[:1800]}'})
        return

    question = payload.get('question') or payload.get('prompt') or 'Codex necesita una respuesta.'
    options = payload.get('options') or payload.get('choices') or []
    lines = [f'{alias} necesita tu respuesta.', '', question, '']
    keyboard = []
    pending = load_pending()
    mapped = []

    for opt in options:
        if isinstance(opt, dict):
            label = opt.get('label') or opt.get('title') or opt.get('value') or 'Opción'
            desc = opt.get('description') or opt.get('details') or ''
            value = opt.get('value') or label
        else:
            label = str(opt)
            desc = ''
            value = str(opt)
        lines.append(f'- {label}')
        if desc:
            lines.append(f'  {desc}')
        keyboard.append([label])
        mapped.append({'label': label, 'value': value, 'description': desc})

    pending[str(chat_id)] = {
        'alias': alias,
        'question': question,
        'options': mapped,
        'raw': payload,
    }
    save_pending(pending)
    append({'kind': 'reply', 'chat_id': chat_id, 'text': '\n'.join(lines)[:3500], 'keyboard': keyboard})


if __name__ == '__main__':
    pass
