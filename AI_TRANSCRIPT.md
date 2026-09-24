# AI Coding Transcript

## User instruction

Read `Support_Ticketing_Interview_Assignment-1.docx` and `assesment.txt`, then create the full project with minimal necessary text and no unrelated additions.

## Requirements extracted

- FastAPI, PostgreSQL-ready SQLAlchemy backend.
- React and TypeScript frontend.
- Ticket creation, readable number, OPEN default status.
- Status, priority, category and assignee workflow.
- Replies, internal notes and real-time customer-visible messages.
- Audit history for status, priority and assignment changes.
- Filters, validation, seed/demo data, migrations and two automated tests.

## Implementation decisions

- SQLite is the local default so the project runs without requiring a local database server; `DATABASE_URL` switches to PostgreSQL.
- WebSocket connections use an in-memory room manager for the MVP.
- Authentication and bonus features were omitted because they are outside the required scope.
- The UI uses only ticketing actions and the required states.

## Requirement completion pass

- Added agent and customer demo views.
- Added customer-only public messages and blocked customer internal notes.
- Added viewer-aware ticket detail responses and WebSocket rooms.
- Added WebSocket message persistence and public/internal broadcast rules.
- Added assignment validation, readable assignment audit values, status timestamps, and Alembic migrations.
- Added responsive layouts, accessible labels, notifications, loading/empty states, and frontend environment configuration.
- Added automated privacy, customer reply, and WebSocket tests.

