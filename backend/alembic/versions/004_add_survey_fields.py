"""add survey comment and answers columns

Revision ID: 004
Revises: 003
Create Date: 2026-06-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("surveys", sa.Column("comment", sa.Text(), nullable=True))
    op.add_column("surveys", sa.Column("answers", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("surveys", "answers")
    op.drop_column("surveys", "comment")
