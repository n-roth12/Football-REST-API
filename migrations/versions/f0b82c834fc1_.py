"""empty message

Revision ID: f0b82c834fc1
Revises: 
Create Date: 2022-04-25 22:48:55.405787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0b82c834fc1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dst',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team', sa.String(length=5), nullable=True),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.Column('city', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('position', sa.String(length=3), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('update',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), server_default='2022-04-25 22:48:53.917426', nullable=True),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=True),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('password', sa.String(length=256), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('public_id')
    )
    op.create_table('dst_game_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dst_id', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('game', sa.String(length=10), nullable=True),
    sa.Column('sacks', sa.Float(), nullable=True),
    sa.Column('interceptions', sa.Integer(), nullable=True),
    sa.Column('safeties', sa.Integer(), nullable=True),
    sa.Column('fumble_recoveries', sa.Integer(), nullable=True),
    sa.Column('blocks', sa.Integer(), nullable=True),
    sa.Column('touchdowns', sa.Integer(), nullable=True),
    sa.Column('points_against', sa.Integer(), nullable=True),
    sa.Column('passing_yards_against', sa.Integer(), nullable=True),
    sa.Column('rushing_yards_against', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dst_id'], ['dst.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player_game_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('team', sa.String(length=4), nullable=True),
    sa.Column('game', sa.String(length=10), nullable=True),
    sa.Column('passing_attempts', sa.Integer(), nullable=True),
    sa.Column('passing_completions', sa.Integer(), nullable=True),
    sa.Column('passing_yards', sa.Integer(), nullable=True),
    sa.Column('passing_touchdowns', sa.Integer(), nullable=True),
    sa.Column('passing_interceptions', sa.Integer(), nullable=True),
    sa.Column('passing_2point_conversions', sa.Integer(), nullable=True),
    sa.Column('rushing_attempts', sa.Integer(), nullable=True),
    sa.Column('rushing_yards', sa.Integer(), nullable=True),
    sa.Column('rushing_touchdowns', sa.Integer(), nullable=True),
    sa.Column('rushing_2point_conversions', sa.Integer(), nullable=True),
    sa.Column('receptions', sa.Integer(), nullable=True),
    sa.Column('recieving_yards', sa.Integer(), nullable=True),
    sa.Column('recieving_touchdowns', sa.Integer(), nullable=True),
    sa.Column('recieving_2point_conversions', sa.Integer(), nullable=True),
    sa.Column('fumbles_lost', sa.Integer(), nullable=True),
    sa.Column('fantasy_points', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['player.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player_game_stats')
    op.drop_table('dst_game_stats')
    op.drop_table('user')
    op.drop_table('update')
    op.drop_table('player')
    op.drop_table('dst')
    # ### end Alembic commands ###
