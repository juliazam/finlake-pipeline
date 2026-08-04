"""backfill payment_method to unknown

Revision ID: ccb50a67ac67
Revises: fc502924eaf0
Create Date: 2026-07-27 15:40:43.539098

"""
# pylint: disable=no-member
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ccb50a67ac67'
down_revision: Union[str, Sequence[str], None] = 'fc502924eaf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE transactions SET payment_method = 'unknown' WHERE payment_method IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: The rollback is not reversible correctly — it is impossible to distinguish
    # between records whose payment_method was NULL before this migration and those that were
    # initially 'unknown'.
    op.execute("UPDATE transactions SET payment_method = NULL WHERE payment_method = 'unknown'")
