"""add project

Revision ID: 2ad39b3ab779
Revises: ae7cac779f95
Create Date: 2021-06-10 21:06:41.959977

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2ad39b3ab779"
down_revision = "ae7cac779f95"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "project",
        sa.Column("id", postgresql.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("manager_id", postgresql.UUID(), nullable=True),
        sa.Column("programme_id", postgresql.UUID(), nullable=True),
        sa.Column("organisation_id", postgresql.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["manager_id"], ["person.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisation.id"],
        ),
        sa.ForeignKeyConstraint(
            ["programme_id"],
            ["programme.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_created_at"), "project", ["created_at"], unique=False)
    op.create_index(op.f("ix_project_manager_id"), "project", ["manager_id"], unique=False)
    op.create_index(op.f("ix_project_name"), "project", ["name"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_project_name"), table_name="project")
    op.drop_index(op.f("ix_project_manager_id"), table_name="project")
    op.drop_index(op.f("ix_project_created_at"), table_name="project")
    op.drop_table("project")
    # ### end Alembic commands ###
