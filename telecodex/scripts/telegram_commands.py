#!/usr/bin/env python3
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME = BASE_DIR / 'runtime'
INBOX = RUNTIME / 'inbox.jsonl'
EVENTS = RUNTIME / 'events.jsonl'
OUTBOX = RUNTIME / 'outbox.jsonl'
CODEX_SESSIONS = RUNTIME / 'codex_sessions.json'
PENDING = RUNTIME / 'pending_codex_actions.json'
MONITORS = RUNTIME / 'session_monitors.json'
PENDING_UI = RUNTIME / 'pending_ui_requests.json'
SEND_CODEX = BASE_DIR / 'scripts' / 'send_codex_message.py'
SEND_CODEX_FRESH = BASE_DIR / 'scripts' / 'send_codex_fresh.py'
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


def load_codex_sessions():
    if not CODEX_SESSIONS.exists():
        return []
    try:
        return json.loads(CODEX_SESSIONS.read_text(encoding='utf-8'))
    except Exception:
        return []


def resolve_codex_session(alias: str):
    for s in load_codex_sessions():
        if s.get('alias') == alias:
            return s
    return None


def load_pending():
    if PENDING.exists():
        try:
            return json.loads(PENDING.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_pending(data):
    PENDING.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def load_monitors():
    if MONITORS.exists():
        try:
            return json.loads(MONITORS.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_monitors(data):
    MONITORS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def load_pending_ui():
    if PENDING_UI.exists():
        try:
            return json.loads(PENDING_UI.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_pending_ui(data):
    PENDING_UI.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def normalize_text(text: str) -> str:
    lowered = text.strip().lower()
    normalized = unicodedata.normalize('NFD', lowered)
    normalized = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def handle_command(text: str):
    t = text.strip()
    n = normalize_text(text)

    if t in ('/help', '/start'):
        return (
            'Comandos disponibles:\n'
            '- /help: muestra esta ayuda\n'
            '- /status: últimos eventos útiles\n'
            '- /inbox: últimos mensajes recibidos\n'
            '- /last: último evento\n'
            '- /chats: sesiones Codex recientes\n'
            '- /codex C1 <mensaje>: envía un mensaje a una sesión Codex\n'
            '- /codexnew --cwd /ruta <mensaje>: usa una sesión fresca con cwd controlado\n'
            '- /connect C1: sigue ese chat y avisa cuando termine\n'
            '- /disconnect: deja de seguir el chat conectado\n\n'
            'Tip: evita sesiones marcadas como [riesgoso] en /chats.'
        )

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

    if t == '/chats':
        sessions = load_codex_sessions()
        if not sessions:
            return 'No encontré sesiones de Codex indexadas.'
        lines = ['Sesiones Codex recientes:']
        for s in sessions[:8]:
            badge = ' [riesgoso]' if s.get('risky') else ''
            cwd = s.get('cwd') or 'cwd desconocido'
            lines.append(f"- {s['alias']}: {s['thread_name']}{badge} | {cwd} | {s.get('updated_at','sin fecha')}")
        return '\n'.join(lines)

    if n in ('si', 'confirmo', 'ok', 'dale'):
        return {'action': 'codex_confirm'}

    if n in ('no', 'cancelar', 'cancela'):
        return {'action': 'codex_cancel'}

    if t.startswith('/connect '):
        alias = t[len('/connect '):].strip().upper()
        sess = resolve_codex_session(alias)
        if not sess:
            return f'No encontré la sesión {alias}. Usa /chats.'
        return {'action': 'connect_session', 'alias': alias}

    if t == '/disconnect':
        return {'action': 'disconnect_session'}

    if t.startswith('/codexnew '):
        body = t[len('/codexnew '):].strip()
        if not body.startswith('--cwd '):
            return 'Uso: /codexnew --cwd /ruta tu mensaje'
        try:
            rest = body[6:]
            forced_cwd, message = rest.split(' ', 1)
            forced_cwd = forced_cwd.strip()
            message = message.strip()
        except ValueError:
            return 'Uso: /codexnew --cwd /ruta tu mensaje'
        return {'action': 'codexnew_prepare', 'message': message, 'cwd': forced_cwd}

    if t.startswith('/codex '):
        parts = t.split(' ', 2)
        if len(parts) < 3:
            return 'Uso: /codex C1 tu mensaje'
        alias = parts[1].strip().upper()
        message = parts[2].strip()
        forced_cwd = None
        if message.startswith('--cwd '):
            try:
                rest = message[6:]
                forced_cwd, message = rest.split(' ', 1)
                forced_cwd = forced_cwd.strip()
                message = message.strip()
            except ValueError:
                return 'Uso: /codex C1 --cwd /ruta tu mensaje'
        sess = resolve_codex_session(alias)
        if not sess:
            return f'No encontré la sesión {alias}. Usa /chats.'
        if sess.get('risky'):
            return f'Bloqueé {alias} porque parece una sesión sensible del bridge/setup. Usa otra sesión.'
        cwd = forced_cwd or sess.get('cwd') or '(cwd no detectado)'
        return {'action': 'codex_prepare', 'alias': alias, 'message': message, 'cwd': cwd}

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
        chat_id = str(item.get('chat_id'))
        pending_ui = load_pending_ui()
        ui = pending_ui.get(chat_id)
        if ui:
            idx = ui.get('current_index', 0)
            questions = ui.get('questions', [])
            if idx < len(questions):
                selected = None
                current_q = questions[idx]
                for opt in current_q.get('options', []):
                    if text.strip() == opt.get('label'):
                        selected = opt
                        break
                if selected:
                    ui.setdefault('answers', []).append({
                        'header': current_q.get('header'),
                        'id': current_q.get('id'),
                        'label': selected.get('label'),
                        'value': selected.get('value'),
                        'description': selected.get('description'),
                    })
                    ui['current_index'] = idx + 1
                    pending_ui[chat_id] = ui
                    save_pending_ui(pending_ui)
                    if ui['current_index'] < len(questions):
                        next_q = questions[ui['current_index']]
                        lines = [f"Siguiente pregunta ({ui['current_index']+1}/{len(questions)}):", '', next_q.get('header') or 'Pregunta', next_q.get('question') or '', '']
                        keyboard = []
                        for opt in next_q.get('options', []):
                            lines.append(f"- {opt['label']}")
                            if opt.get('description'):
                                lines.append(f"  {opt['description']}")
                            keyboard.append([opt['label']])
                        append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': '\n'.join(lines)[:3500], 'keyboard': keyboard})
                    else:
                        lines = [f"Respuestas capturadas para {ui.get('alias')}:\n"]
                        answer_lines = []
                        for ans in ui.get('answers', []):
                            lines.append(f"- {ans['header']}: {ans['label']}")
                            if ans.get('description'):
                                lines.append(f"  {ans['description']}")
                            answer_lines.append(f"{ans['header']}: {ans['label']}")
                        append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': '\n'.join(lines)[:3500]})

                        resume_text = "Respuestas del cuestionario:\n" + '\n'.join(answer_lines) + "\n\nContinúa usando estas respuestas."
                        append(OUTBOX, {
                            'kind': 'reply',
                            'chat_id': chat_id,
                            'text': 'Reenviando respuestas al hilo de Codex...',
                            'store_as': f'processing:{chat_id}',
                        })
                        subprocess.run([
                            sys.executable,
                            str(SEND_CODEX),
                            '--alias', ui.get('alias'),
                            '--text', resume_text,
                            '--chat-id', chat_id,
                        ], check=False)
                        pending_ui.pop(chat_id, None)
                        save_pending_ui(pending_ui)
                    state['last_inbox_line'] += 1
                    continue
        reply = handle_command(text)
        if isinstance(reply, str) and reply:
            append(OUTBOX, {
                'kind': 'reply',
                'chat_id': item.get('chat_id'),
                'text': reply,
            })
        elif isinstance(reply, dict) and reply.get('action') == 'connect_session':
            chat_id = str(item.get('chat_id'))
            monitors = load_monitors()
            sess = resolve_codex_session(reply['alias'])
            status_text = ''
            last_completed = None
            line_count = 0
            if sess and sess.get('file'):
                try:
                    data = Path(sess['file']).read_text(encoding='utf-8', errors='replace').splitlines()
                    line_count = len(data)
                    recent_msgs = []
                    for raw in reversed(data[-120:]):
                        obj = json.loads(raw)
                        if obj.get('type') == 'event_msg' and (obj.get('payload') or {}).get('type') in ('turn_completed', 'task_complete') and not last_completed:
                            last_completed = obj.get('timestamp')
                        if obj.get('type') == 'event_msg' and (obj.get('payload') or {}).get('type') == 'agent_message':
                            msg = (obj.get('payload') or {}).get('message')
                            if msg:
                                recent_msgs.append(msg)
                        if last_completed and len(recent_msgs) >= 2:
                            break
                    recent_msgs.reverse()
                    if recent_msgs:
                        status_text = '\n\nMensajes recientes:\n' + '\n\n'.join(recent_msgs[-2:])[:1500]
                except Exception:
                    pass
            monitors[chat_id] = {'alias': reply['alias'], 'last_completed': last_completed, 'line_count': line_count}
            save_monitors(monitors)
            append(OUTBOX, {
                'kind': 'reply',
                'chat_id': chat_id,
                'text': f"Conectado a {reply['alias']}. Te avisaré cuando ese chat termine un turno nuevo.{status_text}",
            })
        elif isinstance(reply, dict) and reply.get('action') == 'disconnect_session':
            chat_id = str(item.get('chat_id'))
            monitors = load_monitors()
            if monitors.pop(chat_id, None) is not None:
                save_monitors(monitors)
                append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': 'Desconectado del chat monitoreado.'})
            else:
                append(OUTBOX, {'kind': 'reply', 'chat_id': chat_id, 'text': 'No había ningún chat conectado.'})
        elif isinstance(reply, dict) and reply.get('action') == 'codexnew_prepare':
            pending = load_pending()
            chat_id = str(item.get('chat_id'))
            pending[chat_id] = {
                'kind': 'fresh',
                'message': reply['message'],
                'cwd': reply['cwd'],
            }
            save_pending(pending)
            append(OUTBOX, {
                'kind': 'reply',
                'chat_id': chat_id,
                'text': f"Codex fresh usará este directorio:\n{reply['cwd']}\n\nResponde 'sí' para continuar o 'no' para cancelar.",
                'keyboard': [['Sí', 'No']],
            })
        elif isinstance(reply, dict) and reply.get('action') == 'codex_prepare':
            pending = load_pending()
            chat_id = str(item.get('chat_id'))
            pending[chat_id] = {
                'alias': reply['alias'],
                'message': reply['message'],
                'cwd': reply['cwd'],
            }
            save_pending(pending)
            append(OUTBOX, {
                'kind': 'reply',
                'chat_id': chat_id,
                'text': f"La sesión {reply['alias']} usará este directorio:\n{reply['cwd']}\n\nResponde 'sí' para continuar o 'no' para cancelar.",
                'keyboard': [['Sí', 'No']],
            })
        elif isinstance(reply, dict) and reply.get('action') == 'codex_confirm':
            pending = load_pending()
            chat_id = str(item.get('chat_id'))
            action = pending.get(chat_id)
            if action:
                append(OUTBOX, {
                    'kind': 'reply',
                    'chat_id': chat_id,
                    'text': 'Procesando...',
                    'store_as': f'processing:{chat_id}',
                })
                if action.get('kind') == 'fresh':
                    subprocess.run([
                        sys.executable,
                        str(SEND_CODEX_FRESH),
                        '--text', action['message'],
                        '--chat-id', chat_id,
                        '--cwd', action['cwd'],
                    ], check=False)
                else:
                    subprocess.run([
                        sys.executable,
                        str(SEND_CODEX),
                        '--alias', action['alias'],
                        '--text', action['message'],
                        '--chat-id', chat_id,
                        '--cwd', action['cwd'],
                    ], check=False)
                pending.pop(chat_id, None)
                save_pending(pending)
            else:
                append(OUTBOX, {
                    'kind': 'reply',
                    'chat_id': chat_id,
                    'text': 'No tengo ninguna acción pendiente para confirmar.',
                })
        elif isinstance(reply, dict) and reply.get('action') == 'codex_cancel':
            pending = load_pending()
            chat_id = str(item.get('chat_id'))
            if pending.pop(chat_id, None) is not None:
                save_pending(pending)
                append(OUTBOX, {
                    'kind': 'reply',
                    'chat_id': chat_id,
                    'text': 'Acción cancelada.',
                })
            else:
                append(OUTBOX, {
                    'kind': 'reply',
                    'chat_id': chat_id,
                    'text': 'No tengo ninguna acción pendiente para cancelar.',
                })
        state['last_inbox_line'] += 1
    save_state(state)


if __name__ == '__main__':
    main()
