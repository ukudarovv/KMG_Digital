"""add adaptation tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-09

"""

from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from app.core.database import Base
    import app.models  # noqa: F401

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    op.drop_table("development_recommendations")
    op.drop_table("learning_modules")
    op.drop_table("smart_goals")
    op.drop_table("one_to_one_meetings")
