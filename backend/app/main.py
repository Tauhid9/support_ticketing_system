from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import Category, MessageType, Priority, Status, Ticket, TicketMessage, User
from .schemas import MessageCreate, TicketCreate, TicketDetail, TicketList, TicketOut, TicketPatch, UserOut
from .services import apply_patch, next_ticket_number, serialize_message

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Badi Support Ticketing")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ConnectionManager:
    def __init__(self): self.rooms = {}
    async def connect(self, ticket_id, websocket):
        await websocket.accept(); self.rooms.setdefault(ticket_id, []).append(websocket)
    def disconnect(self, ticket_id, websocket):
        if ticket_id in self.rooms and websocket in self.rooms[ticket_id]: self.rooms[ticket_id].remove(websocket)
    async def broadcast(self, ticket_id, payload):
        for ws in list(self.rooms.get(ticket_id, [])):
            await ws.send_json(payload)

manager = ConnectionManager()

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/agents", response_model=list[UserOut])
def agents(db: Session = Depends(get_db)):
    return db.scalars(select(User).where(User.role.in_(["AGENT", "ADMIN"]), User.is_active.is_(True)).order_by(User.name)).all()

@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket = Ticket(ticket_number=next_ticket_number(db), **payload.model_dump())
    db.add(ticket); db.commit(); db.refresh(ticket)
    return ticket

@app.get("/tickets", response_model=TicketList)
def list_tickets(status: Status | None = None, priority: Priority | None = None, category: Category | None = None, assigned_agent_id: str | None = None, search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    query = select(Ticket).order_by(Ticket.updated_at.desc())
    if status: query = query.where(Ticket.status == status)
    if priority: query = query.where(Ticket.priority == priority)
    if category: query = query.where(Ticket.category == category)
    if assigned_agent_id: query = query.where(Ticket.assigned_agent_id == assigned_agent_id)
    if search: query = query.where(or_(Ticket.ticket_number.ilike(f"%{search}%"), Ticket.subject.ilike(f"%{search}%"), Ticket.customer_email.ilike(f"%{search}%")))
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(query).all())
    return TicketList(items=items, total=total, page=page, page_size=page_size)

@app.get("/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket: raise HTTPException(404, "Ticket not found")
    return ticket

@app.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: str, payload: TicketPatch, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket: raise HTTPException(404, "Ticket not found")
    if "assigned_agent_id" not in payload.model_fields_set:
        payload = payload.model_copy(update={"assigned_agent_id": ticket.assigned_agent_id})
    apply_patch(db, ticket, payload); db.commit(); db.refresh(ticket)
    return ticket

@app.post("/tickets/{ticket_id}/messages", response_model=dict, status_code=201)
async def add_message(ticket_id: str, payload: MessageCreate, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket: raise HTTPException(404, "Ticket not found")
    message = TicketMessage(ticket_id=ticket.id, sender_name=payload.sender_name, message=payload.message, message_type=payload.type)
    db.add(message); db.commit(); db.refresh(message)
    data = serialize_message(message)
    if payload.type != MessageType.INTERNAL_NOTE:
        await manager.broadcast(ticket_id, {"event": "new_message", "data": data})
    return data

@app.get("/mock/orders/{order_id}")
def mock_order(order_id: str):
    return {"order_id": order_id, "destination": "Turkey", "package": "10 GB", "status": "completed", "esim_status": "installed"}

@app.websocket("/ws/tickets/{ticket_id}")
async def ticket_socket(websocket: WebSocket, ticket_id: str):
    await manager.connect(ticket_id, websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: manager.disconnect(ticket_id, websocket)
