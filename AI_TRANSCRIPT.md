# Complete AI Coding Session Export

Project: Badi eSIM Support Ticketing Module
Repository: https://github.com/Tauhid9/support_ticketing_system

This file records the complete development conversation and implementation decisions used for the assignment.

## 1. Initial request

User provided:

> Read the DOCX and TXT file and create full project. Keep the text minimal and do not add anything outside the requirements.

The provided files were:

- `Support_Ticketing_Interview_Assignment-1.docx`
- `assesment.txt`

## 2. Requirement extraction

The DOCX required a support ticketing module for Badi eSIM with:

- Customer or agent ticket creation
- Customer email, optional order ID, category, subject, description and priority
- Readable ticket numbers such as `BD-1001`
- `OPEN`, `IN_PROGRESS`, `WAITING_FOR_CUSTOMER`, `WAITING_FOR_PROVIDER`, `RESOLVED`, and `CLOSED` states
- `LOW`, `MEDIUM`, `HIGH`, and `URGENT` priorities
- Categories for installation, activation, connectivity, orders, top-ups, refunds, and other questions
- Conversation history with sender, message type and timestamp
- Customer-visible replies in real time in both directions
- Agent-only internal notes
- Ticket filtering by status, priority, category and assigned agent
- Status, priority and assignee controls
- Status and assignment audit history
- FastAPI, PostgreSQL and SQLAlchemy/SQLModel
- Database migrations
- Validation and error handling
- React and TypeScript frontend
- Loading, empty and error states
- At least two automated tests
- README, seed/demo data, assumptions/trade-offs and more-time improvements
- Complete AI coding transcript if AI tools were used

The TXT file added implementation guidance for the same MVP, including four core tables, REST endpoints, WebSocket messaging, seed data, tests and a focused three-screen interface.

## 3. Initial architecture

The implementation used:

- FastAPI backend
- SQLAlchemy models
- PostgreSQL-compatible configuration
- SQLite default for local development
- React, TypeScript and Vite frontend
- In-memory WebSocket room manager for the single-process MVP
- `users`, `tickets`, `ticket_messages`, and `ticket_events` tables

The initial public API was:

- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}`
- `POST /tickets/{ticket_id}/messages`
- `WS /ws/tickets/{ticket_id}`

## 4. Initial implementation

Created the following project structure:

```text
backend/
  app/
    db.py
    main.py
    models.py
    schemas.py
    services.py
  migrations/001_initial.sql
  seed.py
  tests/test_tickets.py
  requirements.txt
  .env.example
frontend/
  src/main.tsx
  src/styles.css
  package.json
  pnpm-lock.yaml
  vite.config.ts
README.md
AI_TRANSCRIPT.md
.gitignore
```

The first version implemented ticket creation, ticket listing, filters, ticket detail, messages, audit events, seed data, tests and the responsive React interface.

## 5. Verification of the initial implementation

The backend was compiled and dependencies were installed using the workspace runtime.

The initial tests verified:

1. Creating a ticket creates a readable ticket number and starts in `OPEN`.
2. Changing status creates a `STATUS_CHANGED` audit event.

The frontend production build completed successfully with Vite and TypeScript.

## 6. Git setup and repository work

The supplied repository URL was:

```text
https://github.com/Tauhid9/support_ticketing_system.git
```

The project was committed and pushed to `master` first. The remote repository already contained an unrelated initial `main` commit, so `master` was merged into `main` using an unrelated-history merge. The README conflict was resolved in favor of the project README.

The remote `master` branch and local `master` branch were then removed.

The final working branch became `main`.

## 7. First project review

The first review identified these gaps:

- Customer-facing view was missing.
- Internal-note visibility was not enforced by the backend.
- WebSocket connections did not persist incoming WebSocket messages.
- Assignment audit values could show agent IDs instead of names.
- Assignment IDs were not validated.
- Only basic migration support existed.
- Frontend API URL was hardcoded.
- UI errors and accessibility labels needed improvement.
- The first transcript file was only a summary and did not satisfy the complete-transcript requirement.

## 8. Requirement-completion fixes

The following changes were implemented:

### Backend

- Added `viewer=agent|customer` handling for ticket detail responses.
- Customer detail responses exclude internal notes and agent activity events.
- Customer message requests cannot create internal notes.
- WebSocket rooms now track agent and customer viewers separately.
- Internal notes are not broadcast to customer viewers.
- WebSocket messages are validated, persisted and broadcast.
- Customer and agent public replies are supported over WebSocket.
- Assignment IDs are validated against active users.
- Assignment audit entries use readable agent names.
- Resolution and closure timestamps are recorded.
- Ticket numbering no longer relies on raw row count.
- CORS is configurable through `CORS_ORIGINS`.
- Added Alembic configuration and an initial migration revision.

### Frontend

- Added Agent and Customer demo views.
- Added customer ticket list and customer conversation view.
- Added customer reply composer.
- Hid internal-note controls from customers.
- Added accessible labels for filters and controls.
- Added loading spinner, empty state, success notices and error notices.
- Added disabled/loading button states.
- Added responsive layouts for desktop, tablet and mobile widths.
- Added responsive ticket cards for narrow screens.
- Added frontend `.env.example` with `VITE_API_URL`.
- Added page metadata and title.

### Tests

The test suite was expanded to five tests:

1. Ticket creation and `OPEN` status
2. Status audit history
3. Customer cannot see or create internal notes
4. Customer reply is saved and visible
5. WebSocket public reply is saved and broadcast

## 9. Review and visual verification

The local project was run with:

```text
Backend:  http://127.0.0.1:8000
Frontend: http://127.0.0.1:5173
API docs: http://127.0.0.1:8000/docs
```

The following screens were inspected in the local browser:

- Agent ticket list
- Customer ticket list
- Agent ticket detail with status, priority, assignee and activity controls
- Customer ticket detail with internal notes hidden
- Customer create-ticket form

The UI was checked at a narrow viewport and the responsive card layout, navigation, filters, form labels and conversation layout were verified.

## 10. Final verification results

Backend tests:

```text
5 passed
```

Frontend production build:

```text
tsc -b && vite build
completed successfully
```

Alembic migration:

```text
alembic upgrade head
completed successfully on a fresh SQLite database
```

API health:

```json
{"status":"ok"}
```

Git working tree was clean after the final push.

## 11. Known scope and trade-offs

- The Agent/Customer switch is a demo view switch, not a full authentication system. Authentication and role-based access were listed as optional bonus work in the assignment.
- SQLite is the default local database so the project can run without a database server. PostgreSQL is supported through `DATABASE_URL`.
- The WebSocket manager is in-memory and is suitable for one backend process. Redis/pub-sub would be required for multi-instance deployment.
- File attachments, notifications, SLA timers, React Native, Docker and advanced analytics were not added because they were optional bonus ideas.

## 12. Final repository state

The project was committed to the `main` branch and pushed to GitHub.

Final cleanup commit:

```text
ab04aa9 Ignore generated Python caches
```

The repository contains the source code, README, migrations, seed data, tests, environment examples and this transcript export.
