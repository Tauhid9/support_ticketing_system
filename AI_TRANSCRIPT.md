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

