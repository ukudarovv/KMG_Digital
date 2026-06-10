"""add screening decision to department matches

Revision ID: 007
Revises: 006
Create Date: 2026-06-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "department_matches",
        sa.Column("decision", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("department_matches", "decision")
