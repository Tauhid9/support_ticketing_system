import os
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine, get_db
from .models import Category, EventType, MessageType, Priority, Role, Status, Ticket, TicketEvent, TicketMessage, User
from .schemas import EventOut, MessageCreate, MessageOut, TicketCreate, TicketDetail, TicketList, TicketOut, TicketPatch, UserOut
from .services import apply_patch, next_ticket_number, serialize_message

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Badi Support Ticketing")

allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[str, list[tuple[WebSocket, Literal["agent", "customer"]]]] = {}

    async def connect(self, ticket_id: str, websocket: WebSocket, viewer: Literal["agent", "customer"]):
        await websocket.accept()
        self.rooms.setdefault(ticket_id, []).append((websocket, viewer))

    def disconnect(self, ticket_id: str, websocket: WebSocket):
        self.rooms[ticket_id] = [(connection, viewer) for connection, viewer in self.rooms.get(ticket_id, []) if connection is not websocket]

    async def broadcast(self, ticket_id: str, payload: dict):
        message_type = payload.get("data", {}).get("message_type")
        for websocket, viewer in list(self.rooms.get(ticket_id, [])):
            if viewer == "customer" and message_type == MessageType.INTERNAL_NOTE.value:
                continue
            try:
                await websocket.send_json(payload)
            except Exception:
                self.disconnect(ticket_id, websocket)


manager = ConnectionManager()


def ticket_detail(ticket: Ticket, viewer: Literal["agent", "customer"]) -> TicketDetail:
    result = TicketDetail.model_validate(ticket)
    result.messages = [MessageOut.model_validate(message) for message in ticket.messages if viewer == "agent" or message.message_type != MessageType.INTERNAL_NOTE]
    result.events = [EventOut.model_validate(event) for event in ticket.events if viewer == "agent"]
    return result


def save_message(ticket_id: str, payload: MessageCreate, db: Session):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    message = TicketMessage(ticket_id=ticket.id, sender_name=payload.sender_name.strip(), message=payload.message.strip(), message_type=payload.type)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/agents", response_model=list[UserOut])
def agents(db: Session = Depends(get_db)):
    return db.scalars(select(User).where(User.role.in_([Role.AGENT, Role.ADMIN]), User.is_active.is_(True)).order_by(User.name)).all()


@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket = Ticket(ticket_number=next_ticket_number(db), **payload.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/tickets", response_model=TicketList)
def list_tickets(status: Status | None = None, priority: Priority | None = None, category: Category | None = None, assigned_agent_id: str | None = None, search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    query = select(Ticket).order_by(Ticket.updated_at.desc())
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    if category:
        query = query.where(Ticket.category == category)
    if assigned_agent_id:
        query = query.where(Ticket.assigned_agent_id == assigned_agent_id)
    if search:
        term = f"%{search.strip()}%"
        query = query.where(or_(Ticket.ticket_number.ilike(term), Ticket.subject.ilike(term), Ticket.customer_email.ilike(term)))
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    return TicketList(items=items, total=total, page=page, page_size=page_size)


@app.get("/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: str, viewer: Literal["agent", "customer"] = Query("agent"), db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return ticket_detail(ticket, viewer)


@app.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: str, payload: TicketPatch, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    if "assigned_agent_id" not in payload.model_fields_set:
        payload = payload.model_copy(update={"assigned_agent_id": ticket.assigned_agent_id})
    if payload.assigned_agent_id and not db.get(User, payload.assigned_agent_id):
        raise HTTPException(422, "Assigned agent not found")
    apply_patch(db, ticket, payload)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.post("/tickets/{ticket_id}/messages", response_model=dict, status_code=201)
async def add_message(ticket_id: str, payload: MessageCreate, viewer: Literal["agent", "customer"] = Query("agent"), db: Session = Depends(get_db)):
    if viewer == "customer" and payload.type == MessageType.INTERNAL_NOTE:
        raise HTTPException(403, "Customers cannot create internal notes")
    message = save_message(ticket_id, payload, db)
    data = serialize_message(message)
    await manager.broadcast(ticket_id, {"event": "new_message", "data": data})
    return data


@app.get("/mock/orders/{order_id}")
def mock_order(order_id: str):
    return {"order_id": order_id, "destination": "Turkey", "package": "10 GB", "status": "completed", "esim_status": "installed"}


@app.websocket("/ws/tickets/{ticket_id}")
async def ticket_socket(websocket: WebSocket, ticket_id: str):
    requested_viewer = websocket.query_params.get("viewer", "agent")
    viewer: Literal["agent", "customer"] = "customer" if requested_viewer == "customer" else "agent"
    await manager.connect(ticket_id, websocket, viewer)
    try:
        while True:
            incoming = MessageCreate.model_validate(await websocket.receive_json())
            if viewer == "customer" and incoming.type == MessageType.INTERNAL_NOTE:
                await websocket.send_json({"event": "error", "message": "Customers cannot create internal notes"})
                continue
            db = SessionLocal()
            try:
                message = save_message(ticket_id, incoming, db)
                await manager.broadcast(ticket_id, {"event": "new_message", "data": serialize_message(message)})
            finally:
                db.close()
    except WebSocketDisconnect:
        manager.disconnect(ticket_id, websocket)
