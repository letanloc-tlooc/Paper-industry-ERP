"""add warehouse id to purchase orders

Revision ID: a2229e7b697e
Revises: e2a76855206a
Create Date: 2026-09-17 20:48:46.533998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2229e7b697e'
down_revision: Union[str, Sequence[str], None] = 'e2a76855206a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "purchase_orders",
        sa.Column(
            "warehouse_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_purchase_orders_warehouse_id",
        "purchase_orders",
        "warehouses",
        ["warehouse_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "fk_purchase_orders_warehouse_id",
        "purchase_orders",
        type_="foreignkey",
    )

    op.drop_column(
        "purchase_orders",
        "warehouse_id",
    )