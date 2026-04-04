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


def maybe_json(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def emit_request(chat_id: str, alias: str, raw_text: str):
    payload = maybe_json(raw_text)
    if isinstance(payload, dict) and 'arguments' in payload:
        payload = maybe_json(payload['arguments'])
    if not isinstance(payload, dict):
        append({'kind': 'reply', 'chat_id': chat_id, 'text': f'{alias} te está pidiendo respuesta, pero no pude parsear las opciones.\n\n{str(raw_text)[:1800]}'} )
        return

    questions = payload.get('questions') or []
    if not questions:
        append({'kind': 'reply', 'chat_id': chat_id, 'text': f'{alias} te está pidiendo respuesta, pero no encontré preguntas estructuradas.\n\n{json.dumps(payload, ensure_ascii=False)[:1800]}'} )
        return

    pending = load_pending()
    all_buttons = []
    text_blocks = [f'{alias} necesita tu respuesta.']
    first_question_options = []

    for idx, q in enumerate(questions, start=1):
        header = q.get('header') or f'Pregunta {idx}'
        question = q.get('question') or q.get('prompt') or 'Sin pregunta visible'
        text_blocks.append('')
        text_blocks.append(f'{header}')
        text_blocks.append(question)
        options = []
        for opt in q.get('options', []):
            label = opt.get('label') or opt.get('value') or 'Opción'
            desc = opt.get('description') or ''
            value = opt.get('value') or label
            text_blocks.append(f'- {label}')
            if desc:
                text_blocks.append(f'  {desc}')
            options.append({'label': label, 'value': value, 'description': desc})
        if idx == 1:
            first_question_options = options

    for opt in first_question_options:
        all_buttons.append([opt['label']])

    pending[str(chat_id)] = {
        'alias': alias,
        'questions': questions,
        'options': first_question_options,
        'raw': payload,
    }
    save_pending(pending)
    append({'kind': 'reply', 'chat_id': chat_id, 'text': '\n'.join(text_blocks)[:3500], 'keyboard': all_buttons if all_buttons else None})


if __name__ == '__main__':
    pass
