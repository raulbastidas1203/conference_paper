# telecodex en este workspace

Esta carpeta contiene una copia de `Telegram_Notificaciones_Cursor-Codex` para inspección y adaptación.

## Estado actual

- Repo original copiada dentro de `telecodex/`
- Proyecto original pensado para **Windows + PowerShell**
- Este workspace corre en **Linux**, así que no se puede prometer funcionamiento inmediato sin adaptación
- **No** guardes el bot token directamente en archivos versionados

## Lo importante

El valor que a veces se comparte como `123456:ABC...` es un **bot token**, no un `chatId`.

Necesitas ambos:
- `botToken`: secreto del bot de Telegram
- `chatId`: ID numérico del chat donde quieres recibir mensajes

## Recomendación de seguridad

Guarda credenciales por variables de entorno o en archivos locales ignorados por git.

Ejemplo:

```bash
export CODEX_TELEGRAM_BOT_TOKEN='TU_BOT_TOKEN'
export CODEX_TELEGRAM_CHAT_ID='TU_CHAT_ID'
```

## Limitaciones encontradas

- Los scripts son `.ps1`
- La automatización de Cursor depende de hooks/rutas de Windows
- El puente fuerte es para Codex local; Cursor es parcial

## Siguiente paso sugerido

1. Confirmar el `chatId` real
2. Decidir si quieres:
   - portar el watcher a Linux, o
   - usar OpenClaw directamente como puente y solo tomar ideas de esta repo
3. Probar conectividad del bot con un script mínimo de Telegram

## Adaptación Linux añadida

Se añadió un puente mínimo para Linux:

- `requirements.txt`
- `scripts/telegram_bridge.py`
- `scripts/setup_linux.sh`
- `scripts/watcher.py`
- `scripts/emit_event.py`
- `scripts/read_inbox.py`
- `runtime/events.jsonl`
- `runtime/inbox.jsonl`
- `runtime/state.json`

Flujo básico:

```bash
cd telecodex
bash scripts/setup_linux.sh
export CODEX_TELEGRAM_BOT_TOKEN='TU_BOT_TOKEN'
python scripts/telegram_bridge.py get-me
python scripts/telegram_bridge.py get-updates
```

Cuando le escribas al bot desde Telegram, `get-updates` devolverá tu `chat.id`.
Con ese valor ya podremos enviar mensajes de prueba con:

```bash
export CODEX_TELEGRAM_CHAT_ID='TU_CHAT_ID'
python scripts/telegram_bridge.py send --text 'hola desde telecodex'
```

## Nuevo esquema local de eventos

Ahora `telecodex` usa archivos locales como puente:

- `runtime/events.jsonl` → cosas que hizo/está haciendo el agente
- `runtime/inbox.jsonl` → mensajes que llegan desde Telegram
- `runtime/state.json` → cursor interno del watcher

### Emitir un evento

```bash
python scripts/emit_event.py --type progress --text 'Analizando repo'
python scripts/emit_event.py --type waiting --text 'Necesito confirmación para editar config'
python scripts/emit_event.py --type done --text 'Tarea completada'
```

### Correr el watcher una vez

```bash
python scripts/watcher.py --once
```

### Correrlo continuo

```bash
python scripts/watcher.py --interval 3
```

O con el helper:

```bash
bash scripts/run_watcher.sh
```

### Probar ida y vuelta

```bash
bash scripts/test_roundtrip.sh
```

Luego responde al bot y corre:

```bash
python scripts/watcher.py --once
cat runtime/inbox.jsonl
```

### Leer inbox entrante

```bash
python scripts/read_inbox.py
```

### Convertir inbox de Telegram a archivo visible para Cursor

```bash
python scripts/sync_cursor_inbox.py
bash scripts/open_cursor_inbox.sh
```

Esto vuelca los mensajes de `runtime/inbox.jsonl` a:

- `.cursor-telegram/inbox.md`

### Notificar estado manualmente

```bash
bash scripts/notify_status.sh progress 'Analizando archivo X'
bash scripts/notify_status.sh waiting 'Necesito confirmación para cambiar config'
bash scripts/notify_status.sh done 'Terminé la tarea'
```

### Correr telecodex como servicio simple de usuario

```bash
bash scripts/start_telecodex.sh
bash scripts/status_telecodex.sh
bash scripts/stop_telecodex.sh
```

Esto deja corriendo en background:
- `watcher.py`
- `inbox_sync_loop.py`

Logs:
- `logs/watcher.log`
- `logs/inbox_sync.log`

La idea es simple:
- cualquier proceso local escribe eventos en `events.jsonl`
- el watcher los resume y los manda por Telegram
- tus respuestas por Telegram se guardan en `inbox.jsonl`
- `sync_cursor_inbox.py` las transforma en un archivo legible para Cursor
