"""empty message

Revision ID: b0b75d53babf
Revises: fe6d24781ad8
Create Date: 2019-05-27 09:44:20.799622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0b75d53babf'
down_revision = 'fe6d24781ad8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('route_price_service', sa.Column('matatu_registration', sa.Text(), nullable=False))
    op.create_foreign_key(None, 'route_price_service', 'matatu', ['matatu_registration'], ['registration'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'route_price_service', type_='foreignkey')
    op.drop_column('route_price_service', 'matatu_registration')
    # ### end Alembic commands ###
