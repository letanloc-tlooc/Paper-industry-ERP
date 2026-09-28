"""remove warehouse id from purchase orders

Revision ID: a2229e7b697e
Revises: e2a76855206a
Create Date: 2026-09-17 20:48:46.533998

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "a2229e7b697e"
down_revision: Union[str, Sequence[str], None] = "e2a76855206a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass


def downgrade():
    pass