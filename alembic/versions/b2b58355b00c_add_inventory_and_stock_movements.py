"""add inventory and stock movements

Revision ID: b2b58355b00c
Revises: a2229e7b697e
Create Date: 2026-09-19 16:23:15.483084

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "b2b58355b00c"
down_revision: Union[str, Sequence[str], None] = "a2229e7b697e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass