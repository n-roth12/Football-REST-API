"""empty message

Revision ID: 4facbcd3f6b5
Revises: f0b82c834fc1
Create Date: 2022-05-03 20:16:45.015872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4facbcd3f6b5'
down_revision = 'f0b82c834fc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dst_game_stats', sa.Column('fanduel_points', sa.Float(), nullable=True))
    op.add_column('dst_game_stats', sa.Column('draftkings_points', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dst_game_stats', 'draftkings_points')
    op.drop_column('dst_game_stats', 'fanduel_points')
    # ### end Alembic commands ###
