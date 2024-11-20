"""Added platform field to game session table

Revision ID: 6cc6b9a26834
Revises: e9bdaa05c0c5
Create Date: 2024-10-27 22:26:25.171523

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6cc6b9a26834'
down_revision: Union[str, None] = 'e9bdaa05c0c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_sessions', sa.Column('platform', sa.String(), nullable=True))
    op.create_index(op.f('ix_game_sessions_platform'), 'game_sessions', ['platform'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_game_sessions_platform'), table_name='game_sessions')
    op.drop_column('game_sessions', 'platform')
    # ### end Alembic commands ###
