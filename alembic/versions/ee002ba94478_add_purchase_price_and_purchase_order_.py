"""add purchase price and purchase order line total

Revision ID: ee002ba94478
Revises: b2b58355b00c
Create Date: 2026-09-25 13:51:34.714481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ee002ba94478"
down_revision: Union[str, Sequence[str], None] = "b2b58355b00c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "products",
        sa.Column(
            "purchase_price",
            sa.Numeric(15, 2),
            nullable=False,
            server_default=sa.text("0.00"),
        ),
    )

    op.add_column(
        "purchase_order_items",
        sa.Column(
            "line_total",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0.00"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "purchase_order_items",
        "line_total",
    )

    op.drop_column(
        "products",
        "purchase_price",
    )