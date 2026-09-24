# Badi Support Ticketing

Minimal support-ticket MVP for the interview assignment.

## Stack

- FastAPI, SQLAlchemy, PostgreSQL-compatible schema
- React, TypeScript, Vite
- WebSocket ticket rooms

## Run

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

The default local database is SQLite. Set `DATABASE_URL` from `.env.example` for PostgreSQL.

For a fresh database, run `alembic upgrade head` before `python seed.py`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Included

- Ticket creation and readable ticket numbers
- Agent and customer demo views
- Ticket list filters and search
- Status, priority and assignee controls
- Customer-visible replies and internal notes
- Bidirectional WebSocket reply updates
- Customer response privacy: internal notes are agent-only
- Status, priority and assignment audit events
- Seed/demo data
- Automated tests in `backend/tests`
- Initial SQL migration in `backend/migrations/001_initial.sql`

## Tests

```bash
cd backend
pytest
```

## Trade-offs

Authentication, Redis, file uploads and provider integrations are outside the required MVP. The WebSocket manager is in-memory, which is suitable for one process; Redis pub/sub would be the next step for multiple backend instances.

## With more time

Add authentication and role enforcement, PostgreSQL migration tooling, pagination controls, attachment storage, and multi-instance WebSocket broadcasting.

## AI coding transcript

The development session is summarized in `AI_TRANSCRIPT.md`.
