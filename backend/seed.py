from app.db import Base, SessionLocal, engine
from app.models import Category, MessageType, Priority, Role, Status, Ticket, TicketMessage, User

Base.metadata.create_all(bind=engine)
db = SessionLocal()
if not db.query(User).first():
    agents = [User(name="Anas Rahman", email="anas@badi.example", role=Role.AGENT), User(name="Maya Chen", email="maya@badi.example", role=Role.AGENT)]
    db.add_all(agents); db.flush()
    tickets = [
        Ticket(ticket_number="BD-1001", customer_email="sara@example.com", order_id="ORD-10293", category=Category.CONNECTIVITY, subject="eSIM installed but no internet", description="My eSIM is installed but internet is not working.", priority=Priority.HIGH, status=Status.IN_PROGRESS, assigned_agent_id=agents[0].id),
        Ticket(ticket_number="BD-1002", customer_email="mohammed@example.com", order_id="ORD-10294", category=Category.REFUND, subject="Refund request", description="I would like a refund for my unused package.", priority=Priority.MEDIUM, status=Status.OPEN),
        Ticket(ticket_number="BD-1003", customer_email="li@example.com", category=Category.ACTIVATION, subject="Activation code not received", description="I completed checkout but cannot find my activation code.", priority=Priority.URGENT, status=Status.WAITING_FOR_CUSTOMER, assigned_agent_id=agents[1].id),
    ]
    db.add_all(tickets); db.flush()
    db.add_all([TicketMessage(ticket_id=tickets[0].id, sender_name="Sara Ahmed", message="My eSIM is installed but internet is not working.", message_type=MessageType.CUSTOMER_REPLY), TicketMessage(ticket_id=tickets[0].id, sender_name="Anas Rahman", message="Are you currently in Turkey?", message_type=MessageType.AGENT_REPLY), TicketMessage(ticket_id=tickets[0].id, sender_name="Anas Rahman", message="Escalated to the upstream provider.", message_type=MessageType.INTERNAL_NOTE)])
    db.commit()
db.close()
print("Seed complete")

