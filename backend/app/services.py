from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import EventType, Ticket, TicketEvent, TicketMessage, User


def next_ticket_number(db: Session) -> str:
    numbers = db.scalars(select(Ticket.ticket_number)).all()
    highest = max((int(value.removeprefix("BD-")) for value in numbers if value.startswith("BD-") and value[3:].isdigit()), default=1000)
    return f"BD-{highest + 1}"


def audit(db: Session, ticket: Ticket, event_type: EventType, old_value: str | None, new_value: str | None, actor_name: str = "Support agent", actor_id: str | None = None) -> None:
    db.add(TicketEvent(ticket_id=ticket.id, actor_id=actor_id, actor_name=actor_name, event_type=event_type, old_value=old_value, new_value=new_value))


def apply_patch(db: Session, ticket: Ticket, patch, actor_name: str = "Support agent") -> None:
    if patch.status and patch.status != ticket.status:
        old = ticket.status.value
        ticket.status = patch.status
        audit(db, ticket, EventType.STATUS_CHANGED, old, patch.status.value, actor_name)
        if patch.status.value == "RESOLVED":
            from .models import now
            ticket.resolved_at = now()
        elif patch.status.value == "CLOSED":
            from .models import now
            ticket.closed_at = now()
    if patch.priority and patch.priority != ticket.priority:
        old = ticket.priority.value
        ticket.priority = patch.priority
        audit(db, ticket, EventType.PRIORITY_CHANGED, old, patch.priority.value, actor_name)
    if patch.assigned_agent_id != ticket.assigned_agent_id:
        old_agent = db.get(User, ticket.assigned_agent_id) if ticket.assigned_agent_id else None
        new_agent = db.get(User, patch.assigned_agent_id) if patch.assigned_agent_id else None
        event_type = EventType.REASSIGNED if old_agent else EventType.ASSIGNED
        old_name = old_agent.name if old_agent else "Unassigned"
        new_name = new_agent.name if new_agent else "Unassigned"
        ticket.assigned_agent_id = patch.assigned_agent_id
        audit(db, ticket, event_type, old_name, new_name, actor_name)


def serialize_message(message: TicketMessage) -> dict:
    return {
        "id": message.id,
        "sender_name": message.sender_name,
        "message": message.message,
        "message_type": message.message_type.value,
        "created_at": message.created_at.isoformat(),
    }
