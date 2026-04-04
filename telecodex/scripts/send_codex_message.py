#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME = BASE_DIR / 'runtime'
SESSIONS_JSON = RUNTIME / 'codex_sessions.json'
EVENTS = RUNTIME / 'events.jsonl'
OUTBOX = RUNTIME / 'outbox.jsonl'
LOGS = BASE_DIR / 'logs'
CODEX_BIN = Path.home() / '.cursor' / 'extensions' / 'openai.chatgpt-26.325.31654-linux-x64' / 'bin' / 'linux-x86_64' / 'codex'
WORKDIR = Path('/home/raul/CLAUDE/openclaw')


def append_jsonl(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def load_sessions():
    if not SESSIONS_JSON.exists():
        return []
    try:
        return json.loads(SESSIONS_JSON.read_text(encoding='utf-8'))
    except Exception:
        return []


def resolve_session(alias: str):
    sessions = load_sessions()
    for s in sessions:
        if s.get('alias') == alias:
            return s
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--alias', required=True)
    p.add_argument('--text', required=True)
    p.add_argument('--chat-id', required=True)
    args = p.parse_args()

    sess = resolve_session(args.alias)
    if not sess:
        append_jsonl(OUTBOX, {'kind': 'reply', 'chat_id': args.chat_id, 'text': f'No encontré la sesión {args.alias}. Usa /chats.'})
        return

    session_id = sess['id']
    thread_name = sess.get('thread_name', session_id)
    append_jsonl(EVENTS, {'type': 'progress', 'text': f'Enviando mensaje a {args.alias}: {thread_name}'})

    if not CODEX_BIN.exists():
        append_jsonl(OUTBOX, {'kind': 'reply', 'chat_id': args.chat_id, 'text': 'No encontré el binario de Codex en la extensión de Cursor.'})
        return

    LOGS.mkdir(parents=True, exist_ok=True)
    output_file = LOGS / f'codex-last-{session_id}.txt'
    cmd = [
        str(CODEX_BIN),
        '-C', str(WORKDIR),
        'exec', 'resume', session_id, '-',
        '--json',
        '--dangerously-bypass-approvals-and-sandbox',
        '-o', str(output_file),
    ]

    proc = subprocess.run(cmd, input=args.text, text=True, capture_output=True)

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or 'sin detalle').strip()[-1200:]
        append_jsonl(EVENTS, {'type': 'error', 'text': f'Falló envío a {args.alias}', 'stderr_tail': tail})
        append_jsonl(OUTBOX, {'kind': 'reply', 'chat_id': args.chat_id, 'text': f'Falló enviar a {args.alias}.\n\n{tail}'})
        return

    final_text = ''
    if output_file.exists():
        final_text = output_file.read_text(encoding='utf-8', errors='replace').strip()
    if not final_text:
        final_text = 'Mensaje enviado a Codex, pero no capturé respuesta final todavía.'

    append_jsonl(EVENTS, {'type': 'done', 'text': f'Respuesta recibida de {args.alias}: {thread_name}'})
    append_jsonl(OUTBOX, {'kind': 'reply', 'chat_id': args.chat_id, 'text': f'{args.alias} · {thread_name}\n\n{final_text[:3500]}'})


if __name__ == '__main__':
    main()
