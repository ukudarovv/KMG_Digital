"""add vnd documents and task vnd fields

Revision ID: 005
Revises: 004
Create Date: 2026-06-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

onboarding_stage_enum = postgresql.ENUM(
    "preparation",
    "introduction",
    "engagement",
    "adaptation",
    "retention",
    name="onboardingstage",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "vnd_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=True),
        sa.Column("bitrix_file_id", sa.Integer(), nullable=True),
        sa.Column("stage", onboarding_stage_enum, nullable=True),
        sa.Column("task_type", sa.String(length=128), nullable=True),
        sa.Column("section_hint", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vnd_documents_code"), "vnd_documents", ["code"], unique=True)
    op.create_index(op.f("ix_vnd_documents_id"), "vnd_documents", ["id"], unique=False)

    op.add_column(
        "onboarding_tasks",
        sa.Column("vnd_document_code", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "onboarding_tasks",
        sa.Column("external_link", sa.String(length=1024), nullable=True),
    )
    op.add_column(
        "onboarding_tasks",
        sa.Column("confirmation_required", sa.Boolean(), server_default="false", nullable=False),
    )

    op.add_column(
        "culture_fit_nudges",
        sa.Column("vnd_document_code", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("culture_fit_nudges", "vnd_document_code")
    op.drop_column("onboarding_tasks", "confirmation_required")
    op.drop_column("onboarding_tasks", "external_link")
    op.drop_column("onboarding_tasks", "vnd_document_code")
    op.drop_index(op.f("ix_vnd_documents_id"), table_name="vnd_documents")
    op.drop_index(op.f("ix_vnd_documents_code"), table_name="vnd_documents")
    op.drop_table("vnd_documents")
