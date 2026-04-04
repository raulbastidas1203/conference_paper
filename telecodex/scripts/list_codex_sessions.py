#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

CODEX_HOME = Path.home() / '.codex'
INDEX = CODEX_HOME / 'session_index.jsonl'
SESSIONS_ROOT = CODEX_HOME / 'sessions'
OUT = Path('/home/raul/CLAUDE/openclaw/telecodex/runtime/codex_sessions.json')


def parse_ts(value: str) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
    except Exception:
        return 0.0


def find_session_file(session_id: str) -> Path | None:
    if not session_id or not SESSIONS_ROOT.exists():
        return None
    matches = list(SESSIONS_ROOT.rglob(f'*{session_id}.jsonl'))
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def load_index_sessions():
    rows = []
    if not INDEX.exists():
        return rows
    for line in INDEX.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except Exception:
            continue
        session_id = item.get('id')
        file_path = find_session_file(session_id)
        file_mtime = file_path.stat().st_mtime if file_path and file_path.exists() else 0.0
        updated_at = item.get('updated_at') or ''
        updated_ts = parse_ts(updated_at)
        thread_name = item.get('thread_name') or '(sin título)'
        lowered = thread_name.lower()
        risky = any(k in lowered for k in [
            'telecodex', 'telegram', 'cursor-codex', 'openclaw', 'bridge', 'watcher'
        ])
        rows.append({
            'id': session_id,
            'thread_name': thread_name,
            'updated_at': updated_at,
            'updated_ts': max(updated_ts, file_mtime),
            'file': str(file_path) if file_path else None,
            'risky': risky,
        })
    rows.sort(key=lambda x: x.get('updated_ts', 0.0), reverse=True)
    return rows


def main():
    sessions = load_index_sessions()
    mapped = []
    for i, s in enumerate(sessions[:20], start=1):
        mapped.append({
            'alias': f'C{i}',
            'id': s['id'],
            'thread_name': s['thread_name'],
            'updated_at': s['updated_at'],
            'file': s['file'],
            'risky': s.get('risky', False),
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(mapped, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(mapped[:10], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
