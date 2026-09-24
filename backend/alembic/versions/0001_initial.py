from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("role", sa.String(20), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("tickets", sa.Column("id", sa.String(36), primary_key=True), sa.Column("ticket_number", sa.String(20), nullable=False, unique=True), sa.Column("customer_id", sa.String(36), sa.ForeignKey("users.id")), sa.Column("customer_email", sa.String(255), nullable=False), sa.Column("order_id", sa.String(80)), sa.Column("category", sa.String(30), nullable=False), sa.Column("subject", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("priority", sa.String(20), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("assigned_agent_id", sa.String(36), sa.ForeignKey("users.id")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.Column("resolved_at", sa.DateTime(timezone=True)), sa.Column("closed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_tickets_filters", "tickets", ["status", "priority", "category", "assigned_agent_id"])
    op.create_table("ticket_messages", sa.Column("id", sa.String(36), primary_key=True), sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False), sa.Column("sender_id", sa.String(36), sa.ForeignKey("users.id")), sa.Column("sender_name", sa.String(120), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("message_type", sa.String(30), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_ticket_messages_ticket_id", "ticket_messages", ["ticket_id"])
    op.create_table("ticket_events", sa.Column("id", sa.String(36), primary_key=True), sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False), sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id")), sa.Column("actor_name", sa.String(120), nullable=False), sa.Column("event_type", sa.String(30), nullable=False), sa.Column("old_value", sa.String(120)), sa.Column("new_value", sa.String(120)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_ticket_events_ticket_id", "ticket_events", ["ticket_id"])

def downgrade():
    op.drop_index("ix_ticket_events_ticket_id", table_name="ticket_events")
    op.drop_table("ticket_events")
    op.drop_index("ix_ticket_messages_ticket_id", table_name="ticket_messages")
    op.drop_table("ticket_messages")
    op.drop_index("ix_tickets_filters", table_name="tickets")
    op.drop_table("tickets")
    op.drop_table("users")
