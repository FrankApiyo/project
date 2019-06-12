"""empty message

Revision ID: 338aa11af0be
Revises: b00bd8ded52c
Create Date: 2019-06-12 13:57:47.750781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '338aa11af0be'
down_revision = 'b00bd8ded52c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticket', sa.Column('balance', sa.Float(), nullable=False))
    op.add_column('traveler', sa.Column('outstanding', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('traveler', 'outstanding')
    op.drop_column('ticket', 'balance')
    # ### end Alembic commands ###
