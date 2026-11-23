# Chess Club Snack Rota

## Summary
Chess club members need a shared, easy-to-update list of who brings snacks on which date. This app provides a no-login, server-rendered page where anyone with the link can add, view, complete and delete snack rota entries. The outcome is a single always-current list that persists across reloads.

## Similar initiatives
- **P-t01: Another POC project (tracker) (fastapi-crud)** — Same stack and tracker category; reuse its FastAPI + Jinja2 + Firestore CRUD pattern as the structural baseline for this rota.
- **P-t04: Another POC project (tracker) (nextjs-crud)** — Same tracker idea but a different stack; we do *not* follow its Next.js approach and stay on server-rendered FastAPI pages.
- **P-t06: Another POC project (workflow) (form-workflow)** — Different category and stack; no multi-step workflow is needed here, so nothing is reused beyond the general "form posts to server" idea.

## Scope
1. **Add a rota entry**
   - *As a club member, I want to add an entry with a date, member name and snack so the rota is updated.*
   - Given the add form, When I submit a valid date, member name and snack, Then a new entry appears in the list.
   - Given an empty required field, When I submit, Then the entry is not created and I see a validation message.

2. **List upcoming entries sorted by date**
   - *As a club member, I want to see entries sorted by soonest date so I know who is next.*
   - Given one or more entries exist, When I open the home page, Then entries are displayed sorted by date ascending.
   - Given I reload the page, When it renders, Then previously added entries are still shown (persisted).

3. **Mark an entry as done**
   - *As a club member, I want to mark an entry as done so completed turns are visible but distinct.*
   - Given an entry, When I mark it done, Then it remains in the list shown greyed out.

4. **Delete an entry**
   - *As a club member, I want to delete an entry so mistakes or cancelled turns are removed.*
   - Given an entry, When I delete it, Then it no longer appears in the list.

## Out of scope
- Logins or user accounts.
- Email or SMS reminders.
- Recurring schedules.
- Editing an entry after creation.
- Storing sensitive personal data.

## Data model
**Collection: `rota_entries`**
| Field | Type | Notes |
|---|---|---|
| id | string | Firestore document ID |
| date | string (ISO `YYYY-MM-DD`) | Rota date; used for sorting |
| member_name | string | Free-text name (no login) |
| snack | string | Snack description |
| done | boolean | Defaults to `false` |
| created_at | timestamp | Server-set at creation |

## Pages and endpoints
| Path | Method | Purpose | Who uses it |
|---|---|---|---|
| `/` | GET | Render page: add form + list of entries sorted by date ascending | Chess club members |
| `/entries` | POST | Create a new rota entry, then redirect to `/` | Chess club members |
| `/entries/{id}/done` | POST | Toggle/mark entry as done, then redirect to `/` | Chess club members |
| `/entries/{id}/delete` | POST | Delete entry, then redirect to `/` | Chess club members |
| `/health` | GET | Template health check (unchanged) | Platform/CI |

## Test plan
**Automated (pytest + FastAPI TestClient, Firestore emulator or mock):**
- `POST /entries` with valid data creates a document and redirects (303/302).
- `POST /entries` with a missing required field returns a validation error and creates nothing.
- `GET /` returns 200 and lists entries in ascending date order.
- `POST /entries/{id}/done` sets `done=true` for that document.
- `POST /entries/{id}/delete` removes the document; it is absent from `GET /`.
- `GET /health` still returns the template's healthy response.

**Manual UAT checklist (staging):**
1. Open `/` and confirm the POC banner is visible.
2. Add an entry with date, member name and snack; confirm it appears.
3. Add a second entry with an earlier date; confirm it sorts above the first.
4. Reload the page; confirm both entries persist.
5. Mark one entry done; confirm it stays visible but appears greyed out.
6. Delete an entry; confirm it disappears.
7. Confirm no login is requested at any point.

## Risks and guardrails
- **No authentication (template rule):** Anyone with the link can edit/delete. Acceptable per spec; do not add auth. Use a plain `member_name` text field, not real login.
- **No sensitive data:** Form labels and help text should discourage entering personal/sensitive info; store only name + snack + date.
- **No outbound HTTP / email / payments (template rule):** Reminders are explicitly out of scope; keep all logic server-local to Firestore.
- **Open delete:** Deletion is permanent with no auth; acceptable for a POC but note it in the UI (simple confirm is optional).
- **Date handling:** Store dates as ISO strings to keep Firestore ordering predictable; sort ascending server-side.
- **Keep template files unchanged:** Preserve the POC banner, `/health` endpoint, Dockerfile and CI files.

## Builder instructions
1. Start from the `fastapi-crud` template. Do **not** modify the banner include, `/health` endpoint, `Dockerfile`, or CI workflow files.
2. In the Firestore access layer (e.g. `app/db.py` or template equivalent), add helpers for the `rota_entries` collection: `list_entries()` (ordered by `date` ascending), `add_entry(date, member_name, snack)`, `set_done(id, done)`, `delete_entry(id)`. Set `created_at` server-side and default `done=false`.
3. In the routes module (e.g. `app/main.py` or `app/routes.py`):
   - `GET /` renders `index.html` with the sorted entries list.
   - `POST /entries` reads form fields (`date`, `member_name`, `snack`), validates they are non-empty, creates the entry, and redirects to `/`.
   - `POST /entries/{id}/done` marks the entry done and redirects to `/`.
   - `POST /entries/{id}/delete` deletes the entry and redirects to `/`.
4. In `templates/index.html` (extending the template's base layout with the POC banner):
   - Add a form posting to `/entries` with a date input, member name text input, and snack text input.
   - Render the entries list/table sorted by date; each row shows date, member name, snack, a "Mark done" form-button (`POST /entries/{id}/done`) and a "Delete" form-button (`POST /entries/{id}/delete`).
   - Apply a greyed-out CSS class (e.g. `.done { opacity: 0.5; text-decoration: line-through; }`) to rows where `done` is true.
5. Add server-side validation so empty required fields re-render the page with a message instead of creating an entry.
6. Add the automated tests listed in the Test plan under the template's `tests/` directory.
7. Run the test suite locally against the Firestore emulator (or mock) and confirm `/health` still passes before handing off.
