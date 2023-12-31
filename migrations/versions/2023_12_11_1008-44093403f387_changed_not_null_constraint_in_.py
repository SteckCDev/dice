"""Changed not-null constraint in transaction table

Revision ID: 44093403f387
Revises: e2e719f621b0
Create Date: 2023-12-11 10:08:35.461374

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '44093403f387'
down_revision: Union[str, None] = 'e2e719f621b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'transactions',
        'btc',
        existing_type=sa.NUMERIC(),
        nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'transactions',
        'btc',
        existing_type=sa.NUMERIC(),
        nullable=False
    )
    # ### end Alembic commands ###
