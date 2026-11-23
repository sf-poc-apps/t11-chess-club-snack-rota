# Chess Club Snack Rota

A no-login, server-rendered FastAPI app where chess club members keep a shared
snack rota: who brings which snack on which date. Anyone with the link can add
an entry, mark it done, or delete it. Entries are sorted by date (soonest first)
and persist across reloads (Firestore in the cloud, in-memory store locally).

## Usage

- Open `/` and use the form to add a date, member name and snack.
- Use "Mark done" to grey out a completed turn (click again to undo).
- Use "Delete" to permanently remove an entry.
- No login, email or reminders; do not enter personal or sensitive data.

## Development

```bash
pip install -r requirements-dev.txt && cp sf-banner.js app/static/sf-banner.js
python -m pytest -q              # run tests
python3 .sf/policy_scan.py       # policy scan (must report zero findings)
uvicorn app.main:app --reload    # local run (health: /healthz and /health)
```
