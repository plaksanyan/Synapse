# Synapse backend

Python REST API using FastAPI, SQLAlchemy and SQLite. Flutter is intentionally not part of this project.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SYNAPSE_SECRET_KEY = "replace-with-a-long-random-secret"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. For the first SQLite release, tables are created automatically. Set `DATABASE_URL` to a SQLAlchemy URL to use another database. For schema versioning use `alembic upgrade head`.

## Authentication and ownership

Register and log in with JSON `{ "email": "you@example.com", "password": "at-least-8-characters" }`. Login returns a bearer JWT. In Swagger, use **Authorize** and paste the token (without the `Bearer ` prefix). Every user resource is scoped to the authenticated user; inaccessible decks and cards return 404.

## Card imports

`POST /decks/{id}/import` accepts `{ "format": "txt|cloze|anki", "text": "..." }`. `format` may be omitted: Anki-style cloze syntax selects the cloze parser; otherwise plain text is used.

- `txt`: cards separated by blank lines; front and back separated by `::` or a tab.
- `cloze`: one `{{c1::answer}}` style deletion per line; one card is generated for each distinct cloze id on a line.
- `anki`: basic tab-separated text export rows. Anki package (`.apkg`) binary import is not implemented.

## Tests

Run `python -m pytest tests -q`. Synaptic engine formulas are pure Python and independent of the API and database.
