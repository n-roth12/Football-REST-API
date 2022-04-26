"""empty message

Revision ID: 7edd89ab2755
Revises: 
Create Date: 2022-04-20 20:19:07.777354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7edd89ab2755'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('update',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), server_default='2022-04-20', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('update')
    # ### end Alembic commands ###