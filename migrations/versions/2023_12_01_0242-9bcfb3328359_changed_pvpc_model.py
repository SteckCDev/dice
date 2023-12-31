# noinspection SpellCheckingInspection
"""Changed PVPC model

Revision ID: 9bcfb3328359
Revises: 58eee7efb708
Create Date: 2023-12-01 02:42:27.199438

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
# noinspection SpellCheckingInspection
revision: str = '9bcfb3328359'
down_revision: Union[str, None] = '58eee7efb708'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'games_pvpc',
        'chat_tg_id',
        existing_type=sa.INTEGER(),
        type_=sa.BIGINT(),
        existing_nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'games_pvpc',
        'chat_tg_id',
        existing_type=sa.BIGINT(),
        type_=sa.INTEGER(),
        existing_nullable=False
    )
    # ### end Alembic commands ###
