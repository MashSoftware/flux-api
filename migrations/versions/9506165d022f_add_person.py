"""add person

Revision ID: 9506165d022f
Revises: 221ccee39de7
Create Date: 2021-05-24 19:19:05.787360

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9506165d022f"
down_revision = "221ccee39de7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "person",
        sa.Column("id", postgresql.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role_id", postgresql.UUID(), nullable=False),
        sa.Column("organisation_id", postgresql.UUID(), nullable=False),
        sa.Column("email_address", sa.String(length=254), nullable=False),
        sa.Column("full_time_equivalent", sa.Float(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organisation_id"], ["organisation.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email_address"),
    )
    op.create_index(op.f("ix_person_created_at"), "person", ["created_at"], unique=False)
    op.create_index(op.f("ix_person_organisation_id"), "person", ["organisation_id"], unique=False)
    op.create_index(op.f("ix_person_role_id"), "person", ["role_id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_person_role_id"), table_name="person")
    op.drop_index(op.f("ix_person_organisation_id"), table_name="person")
    op.drop_index(op.f("ix_person_created_at"), table_name="person")
    op.drop_table("person")
    # ### end Alembic commands ###