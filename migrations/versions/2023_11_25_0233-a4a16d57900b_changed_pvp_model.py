"""Changed PVP model

Revision ID: a4a16d57900b
Revises: b6e58e31b3b8
Create Date: 2023-11-25 02:33:07.012050

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a4a16d57900b'
down_revision: Union[str, None] = 'b6e58e31b3b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'games_pvp',
        'opponent_tg_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'games_pvp',
        'opponent_tg_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )
    # ### end Alembic commands ###
