"""create transactions table

Revision ID: 2857bc2e85d3
Revises: 
Create Date: 2026-07-27 12:12:21.798354

"""
# pylint: disable=no-member
# pylint: disable=not-callable
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2857bc2e85d3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'transactions',
        sa.Column('record_id', sa.Integer, primary_key=True),
        sa.Column('transaction_id', sa.String(20), nullable=False, unique=True),
        sa.Column('account_id', sa.String(10), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=True, server_default='SGD'),
        sa.Column('status',
            sa.Enum('pending', 'completed', 'denied', name='transaction_status'), nullable=False),
        sa.Column('merchant', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('transactions')
    sa.Enum(name='transaction_status').drop(op.get_bind())
