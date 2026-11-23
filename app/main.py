import datetime as dt
import os
import pathlib

from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.store import make_store

BASE = pathlib.Path(__file__).parent
app = FastAPI(title="Chess Club Snack Rota")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
templates.env.globals["sf"] = {"expires": os.environ.get("SF_EXPIRES", ""), "env": os.environ.get("SF_ENV", "local")}
store = make_store()

MAX_LEN = 200
COLLECTION = "rota_entries"


@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "ok"


@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"


def _valid_date(value: str) -> bool:
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


@app.get("/")
def index(request: Request, error: str = ""):
    entries = store.list(COLLECTION, order_by="date")
    return templates.TemplateResponse(request, "index.html", {"entries": entries, "error": error})


@app.post("/entries")
def create_entry(request: Request, date: str = Form(..., max_length=10),
                 member_name: str = Form(..., max_length=MAX_LEN),
                 snack: str = Form(..., max_length=MAX_LEN)):
    date = date.strip()
    member_name = member_name.strip()
    snack = snack.strip()
    error = ""
    if not date or not member_name or not snack:
        error = "All fields are required."
    elif not _valid_date(date):
        error = "Date must be a valid date (YYYY-MM-DD)."
    if error:
        entries = store.list(COLLECTION, order_by="date")
        return templates.TemplateResponse(request, "index.html",
                                         {"entries": entries, "error": error},
                                         status_code=422)
    store.create(COLLECTION, {"date": date, "member_name": member_name,
                              "snack": snack, "done": False})
    return RedirectResponse("/", status_code=303)


@app.post("/entries/{entry_id}/done")
def mark_done(entry_id: str):
    entry = store.get(COLLECTION, entry_id)
    if entry:
        store.update(COLLECTION, entry_id, {"done": not entry.get("done", False)})
    return RedirectResponse("/", status_code=303)


@app.post("/entries/{entry_id}/delete")
def delete_entry(entry_id: str):
    store.delete(COLLECTION, entry_id)
    return RedirectResponse("/", status_code=303)
