"""empty message

Revision ID: e6c8e433e3cb
Revises: 59abaa98ef4a
Create Date: 2022-04-21 12:15:53.792670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6c8e433e3cb'
down_revision = '59abaa98ef4a'
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
    op.create_table('dst_game_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dst_id', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('game', sa.String(length=10), nullable=True),
    sa.Column('fantasy_points', sa.Float(), nullable=True),
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
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dst_game_stats')
    op.drop_table('dst')
    # ### end Alembic commands ###
