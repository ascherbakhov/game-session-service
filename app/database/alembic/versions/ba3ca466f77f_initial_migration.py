"""Initial migration

Revision ID: ba3ca466f77f
Revises: 
Create Date: 2024-10-21 23:36:07.022698

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba3ca466f77f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('session_start', sa.DateTime(), nullable=True),
        sa.Column('session_end', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_game_sessions_id'), 'game_sessions', ['id'], unique=False)
    op.create_index(
        op.f('ix_game_sessions_user_id'), 'game_sessions', ['user_id'], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_game_sessions_user_id'), table_name='game_sessions')
    op.drop_index(op.f('ix_game_sessions_id'), table_name='game_sessions')
    op.drop_table('game_sessions')
    # ### end Alembic commands ###
