"""add practice

Revision ID: ba9704e35cb2
Revises: 73ffdedf5a21
Create Date: 2021-05-12 23:58:10.457630

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ba9704e35cb2"
down_revision = "73ffdedf5a21"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "practice",
        sa.Column("id", postgresql.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("head", sa.String(), nullable=False),
        sa.Column("organisation_id", postgresql.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organisation_id"], ["organisation.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_practice_created_at"), "practice", ["created_at"], unique=False)
    op.create_index(op.f("ix_practice_head"), "practice", ["head"], unique=False)
    op.create_index(op.f("ix_practice_name"), "practice", ["name"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_practice_name"), table_name="practice")
    op.drop_index(op.f("ix_practice_head"), table_name="practice")
    op.drop_index(op.f("ix_practice_created_at"), table_name="practice")
    op.drop_table("practice")
    # ### end Alembic commands ###
