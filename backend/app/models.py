from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def now():
    return datetime.now(timezone.utc)

class Role(str, Enum):
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"

class Status(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_CUSTOMER = "WAITING_FOR_CUSTOMER"
    WAITING_FOR_PROVIDER = "WAITING_FOR_PROVIDER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Category(str, Enum):
    INSTALLATION = "INSTALLATION"
    ACTIVATION = "ACTIVATION"
    CONNECTIVITY = "CONNECTIVITY"
    ORDER = "ORDER"
    TOPUP = "TOPUP"
    REFUND = "REFUND"
    OTHER = "OTHER"

class MessageType(str, Enum):
    CUSTOMER_REPLY = "CUSTOMER_REPLY"
    AGENT_REPLY = "AGENT_REPLY"
    INTERNAL_NOTE = "INTERNAL_NOTE"

class EventType(str, Enum):
    STATUS_CHANGED = "STATUS_CHANGED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    ASSIGNED = "ASSIGNED"
    REASSIGNED = "REASSIGNED"

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.AGENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    customer_email: Mapped[str] = mapped_column(String(255))
    order_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    category: Mapped[Category] = mapped_column(SAEnum(Category))
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[Priority] = mapped_column(SAEnum(Priority), default=Priority.MEDIUM)
    status: Mapped[Status] = mapped_column(SAEnum(Status), default=Status.OPEN)
    assigned_agent_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
    events = relationship("TicketEvent", back_populates="ticket", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_tickets_filters", "status", "priority", "category", "assigned_agent_id"),)

class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"), index=True)
    sender_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    sender_name: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(Text)
    message_type: Mapped[MessageType] = mapped_column(SAEnum(MessageType))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    ticket = relationship("Ticket", back_populates="messages")

class TicketEvent(Base):
    __tablename__ = "ticket_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"), index=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(120))
    event_type: Mapped[EventType] = mapped_column(SAEnum(EventType))
    old_value: Mapped[str | None] = mapped_column(String(120), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    ticket = relationship("Ticket", back_populates="events")

