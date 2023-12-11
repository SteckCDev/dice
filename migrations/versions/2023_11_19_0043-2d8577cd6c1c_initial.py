"""Initial

Revision ID: 2d8577cd6c1c
Revises: 
Create Date: 2023-11-19 00:43:42.098864

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2d8577cd6c1c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'users',
        sa.Column('tg_id', sa.Integer(), nullable=False),
        sa.Column('tg_name', sa.String(), nullable=False),
        sa.Column('balance', sa.Integer(), nullable=False),
        sa.Column('beta_balance', sa.Integer(), nullable=False),
        sa.Column('beta_balance_updated_at', sa.DateTime(), nullable=False),
        sa.Column('card_details', sa.String(), nullable=True),
        sa.Column('btc_wallet_address', sa.String(), nullable=True),
        sa.Column('terms_accepted_at', sa.DateTime(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('tg_id'),
        sa.UniqueConstraint('tg_id')
    )
    op.create_table(
        'games_pvb',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_tg_id', sa.Integer(), nullable=False),
        sa.Column('player_won', sa.Boolean(), nullable=False),
        sa.Column('player_dice', sa.Integer(), nullable=False),
        sa.Column('bot_dice', sa.Integer(), nullable=False),
        sa.Column('bet', sa.Integer(), nullable=False),
        sa.Column('beta_mode', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['player_tg_id'], ['users.tg_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'games_pvp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('creator_tg_id', sa.Integer(), nullable=False),
        sa.Column('opponent_tg_id', sa.Integer(), nullable=False),
        sa.Column('winner_tg_id', sa.Integer(), nullable=True),
        sa.Column('creator_dice', sa.Integer(), nullable=True),
        sa.Column('opponent_dice', sa.Integer(), nullable=True),
        sa.Column('bet', sa.Integer(), nullable=False),
        sa.Column('beta_mode', sa.Boolean(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_tg_id'], ['users.tg_id'], ),
        sa.ForeignKeyConstraint(['opponent_tg_id'], ['users.tg_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'games_pvpc',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_tg_id', sa.Integer(), nullable=False),
        sa.Column('creator_tg_id', sa.Integer(), nullable=False),
        sa.Column('opponent_tg_id', sa.Integer(), nullable=False),
        sa.Column('winner_tg_id', sa.Integer(), nullable=True),
        sa.Column('creator_dices', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('opponent_dices', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('bet', sa.Integer(), nullable=False),
        sa.Column('rounds', sa.Integer(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_tg_id'], ['users.tg_id'], ),
        sa.ForeignKeyConstraint(['opponent_tg_id'], ['users.tg_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_tg_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('rub', sa.Integer(), nullable=False),
        sa.Column('btc_to_rub_currency', sa.Numeric(), nullable=False),
        sa.Column('btc', sa.Numeric(), nullable=False),
        sa.Column('fee', sa.Integer(), nullable=False),
        sa.Column('withdrawal_bank_name', sa.String(), nullable=True),
        sa.Column('withdrawal_card_details', sa.String(), nullable=True),
        sa.Column('withdrawal_btc_wallet', sa.String(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_tg_id'], ['users.tg_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('games_pvpc')
    op.drop_table('games_pvp')
    op.drop_table('games_pvb')
    op.drop_table('users')
    # ### end Alembic commands ###
