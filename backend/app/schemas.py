from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .models import Category, EventType, MessageType, Priority, Status

class TicketCreate(BaseModel):
    customer_email: EmailStr
    order_id: str | None = None
    category: Category
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: Priority = Priority.MEDIUM

class TicketPatch(BaseModel):
    status: Status | None = None
    priority: Priority | None = None
    assigned_agent_id: str | None = None

class MessageCreate(BaseModel):
    message: str = Field(min_length=1)
    type: MessageType
    sender_name: str = "Support agent"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: str
    role: str

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sender_name: str
    message: str
    message_type: MessageType
    created_at: datetime

class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    actor_name: str
    event_type: EventType
    old_value: str | None
    new_value: str | None
    created_at: datetime

class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    ticket_number: str
    customer_email: str
    order_id: str | None
    category: Category
    subject: str
    description: str
    priority: Priority
    status: Status
    assigned_agent_id: str | None
    created_at: datetime
    updated_at: datetime

class TicketDetail(TicketOut):
    messages: list[MessageOut] = []
    events: list[EventOut] = []

class TicketList(BaseModel):
    items: list[TicketOut]
    total: int
    page: int
    page_size: int

