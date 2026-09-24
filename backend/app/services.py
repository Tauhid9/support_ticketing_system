from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models import EventType, MessageType, Ticket, TicketEvent, TicketMessage, User, Status

def next_ticket_number(db: Session):
    count = db.scalar(select(func.count(Ticket.id))) or 0
    return f"BD-{1001 + count}"

def audit(db, ticket, event_type, old_value, new_value, actor_name="Support agent", actor_id=None):
    db.add(TicketEvent(ticket_id=ticket.id, actor_id=actor_id, actor_name=actor_name, event_type=event_type, old_value=old_value, new_value=new_value))

def apply_patch(db, ticket, patch, actor_name="Support agent"):
    if patch.status and patch.status != ticket.status:
        old = ticket.status.value
        ticket.status = patch.status
        audit(db, ticket, EventType.STATUS_CHANGED, old, patch.status.value, actor_name)
    if patch.priority and patch.priority != ticket.priority:
        old = ticket.priority.value
        ticket.priority = patch.priority
        audit(db, ticket, EventType.PRIORITY_CHANGED, old, patch.priority.value, actor_name)
    if patch.assigned_agent_id != ticket.assigned_agent_id:
        old_id = ticket.assigned_agent_id
        if old_id is not None:
            event_type = EventType.REASSIGNED
        else:
            event_type = EventType.ASSIGNED
        old_name = "Unassigned" if old_id is None else old_id
        new_name = "Unassigned" if patch.assigned_agent_id is None else patch.assigned_agent_id
        ticket.assigned_agent_id = patch.assigned_agent_id
        audit(db, ticket, event_type, old_name, new_name, actor_name)

def serialize_message(message):
    return {"id": message.id, "sender_name": message.sender_name, "message": message.message, "message_type": message.message_type.value, "created_at": message.created_at.isoformat()}

