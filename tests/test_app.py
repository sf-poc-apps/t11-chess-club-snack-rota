from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _reset():
    from app.main import store
    for entry in store.list("rota_entries"):
        store.delete("rota_entries", entry["id"])


def _add(date, member_name, snack):
    r = client.post("/entries", data={"date": date, "member_name": member_name, "snack": snack},
                    follow_redirects=False)
    assert r.status_code == 303
    return r


def test_health():
    assert client.get("/healthz").text == "ok"


def test_health_template_endpoint():
    assert client.get("/health").text == "ok"


def test_banner_on_index():
    r = client.get("/")
    assert r.status_code == 200
    assert "sf-banner.js" in r.text


def test_create_entry_creates_and_redirects():
    _reset()
    _add("2026-12-01", "Amina", "brownies")
    r = client.get("/")
    assert "Amina" in r.text and "brownies" in r.text


def test_create_entry_missing_field_fails():
    _reset()
    r = client.post("/entries", data={"date": "2026-12-01", "member_name": "", "snack": "chips"},
                    follow_redirects=False)
    assert r.status_code == 422
    assert "required" in r.text.lower()
    body = client.get("/").text
    assert "No rota entries yet" in body  # nothing was created


def test_create_entry_invalid_date_fails():
    _reset()
    r = client.post("/entries", data={"date": "not-a-date", "member_name": "Sam", "snack": "pretzels"},
                    follow_redirects=False)
    assert r.status_code == 422
    assert "valid date" in r.text.lower()


def test_list_sorted_by_date_ascending():
    _reset()
    _add("2026-12-15", "Later", "cookies")
    _add("2026-11-20", "Sooner", "fruit")
    body = client.get("/").text
    assert body.find("Sooner") < body.find("Later")


def test_persistence_across_requests():
    _reset()
    _add("2026-10-05", "Persistent", "popcorn")
    assert "Persistent" in client.get("/").text
    assert "Persistent" in client.get("/").text


def test_mark_done_and_greyed_out():
    _reset()
    _add("2026-12-02", "Ben", "cake")
    from app.main import store
    entry_id = store.list("rota_entries")[0]["id"]
    r = client.post(f"/entries/{entry_id}/done", follow_redirects=False)
    assert r.status_code == 303
    assert store.get("rota_entries", entry_id)["done"] is True
    assert 'class="done"' in client.get("/").text


def test_mark_done_toggle_undoes():
    _reset()
    _add("2026-12-03", "Carla", "nuts")
    from app.main import store
    entry_id = store.list("rota_entries")[0]["id"]
    client.post(f"/entries/{entry_id}/done")
    r = client.post(f"/entries/{entry_id}/done", follow_redirects=False)
    assert r.status_code == 303
    assert store.get("rota_entries", entry_id)["done"] is False


def test_delete_entry():
    _reset()
    _add("2026-12-04", "Dana", "juice")
    from app.main import store
    entry_id = store.list("rota_entries")[0]["id"]
    r = client.post(f"/entries/{entry_id}/delete", follow_redirects=False)
    assert r.status_code == 303
    body = client.get("/").text
    assert "Dana" not in body
