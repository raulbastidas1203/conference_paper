#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME = BASE_DIR / 'runtime'
SESSIONS_JSON = RUNTIME / 'codex_sessions.json'
MONITORS = RUNTIME / 'session_monitors.json'
OUTBOX = RUNTIME / 'outbox.jsonl'
REQUEST_UI = BASE_DIR / 'scripts' / 'request_ui.py'


def append(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
    return default


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def load_sessions():
    return load_json(SESSIONS_JSON, [])


def resolve(alias: str):
    for s in load_sessions():
        if s.get('alias') == alias:
            return s
    return None


def extract_tail_events(file_path: Path, start_line: int):
    if not file_path.exists():
        return None
    lines = file_path.read_text(encoding='utf-8', errors='replace').splitlines()
    new_lines = lines[start_line:]
    events = []
    last_completed = None
    for line in new_lines:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        t = obj.get('type')
        payload = obj.get('payload') or {}
        if t == 'event_msg' and payload.get('type') == 'task_started':
            events.append({'kind': 'task_started', 'timestamp': obj.get('timestamp')})
        elif t == 'event_msg' and payload.get('type') == 'agent_message':
            msg = payload.get('message')
            if msg:
                events.append({'kind': 'agent_message', 'message': msg, 'timestamp': obj.get('timestamp')})
        elif t == 'event_msg' and payload.get('type') in ('turn_completed', 'task_complete'):
            last_completed = obj.get('timestamp')
            events.append({'kind': 'task_complete', 'message': payload.get('last_agent_message'), 'timestamp': obj.get('timestamp')})
        elif t == 'response_item':
            ptype = payload.get('type')
            if ptype in ('custom_tool_call', 'function_call'):
                name = payload.get('name') or payload.get('namespace') or 'tool'
                raw = json.dumps(payload, ensure_ascii=False)
                low = raw.lower()
                if str(name).lower() == 'request_user_input':
                    question = payload.get('arguments') or raw
                    events.append({'kind': 'needs_user_reply', 'name': name, 'raw': str(question)[:1600], 'timestamp': obj.get('timestamp')})
                elif any(k in low for k in ['do you want to run this command', 'allow once', 'waiting for approval', 'requested approval', 'needs approval']):
                    events.append({'kind': 'needs_decision', 'name': name, 'raw': raw[:1600], 'timestamp': obj.get('timestamp')})
                else:
                    events.append({'kind': 'tool_call', 'name': name, 'timestamp': obj.get('timestamp')})
            elif ptype == 'message':
                raw = json.dumps(payload, ensure_ascii=False)
                low = raw.lower()
                if any(k in low for k in ['do you want to run this command', 'allow once', 'waiting for approval', 'requested approval', 'needs approval']):
                    events.append({'kind': 'needs_decision', 'name': 'message', 'raw': raw[:1600], 'timestamp': obj.get('timestamp')})
    return {'events': events, 'line_count': len(lines), 'last_completed': last_completed}


def tick():
    monitors = load_json(MONITORS, {})
    changed = False
    for chat_id, mon in list(monitors.items()):
        alias = mon.get('alias')
        sess = resolve(alias)
        if not sess or not sess.get('file'):
            continue
        prev_lines = mon.get('line_count', 0)
        status = extract_tail_events(Path(sess['file']), prev_lines)
        if not status:
            continue
        events = status.get('events') or []
        if status.get('line_count', 0) != prev_lines:
            mon['line_count'] = status['line_count']
            changed = True
        for ev in events:
            if ev['kind'] == 'task_started':
                append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': f'{alias} recibió un nuevo prompt y empezó a trabajar.'})
            elif ev['kind'] == 'agent_message':
                append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': f'{alias} · progreso:\n\n{ev["message"][:1200]}'})
            elif ev['kind'] == 'tool_call':
                append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': f'{alias} está usando: {ev["name"]}'})
            elif ev['kind'] == 'needs_decision':
                append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': f'{alias} está esperando una decisión o aprobación.\n\nDetalle:\n{ev["raw"][:1400]}'})
            elif ev['kind'] == 'needs_user_reply':
                subprocess.run([sys.executable, str(REQUEST_UI)], check=False)
                from request_ui import emit_request
                emit_request(str(chat_id), alias, ev['raw'])
            elif ev['kind'] == 'task_complete':
                mon['last_completed'] = ev.get('timestamp')
                changed = True
                text = f'{alias} terminó de trabajar.'
                if ev.get('message'):
                    text += f'\n\nRespuesta final:\n{ev["message"][:1800]}'
                append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': text})
    if changed:
        save_json(MONITORS, monitors)


if __name__ == '__main__':
    tick()
