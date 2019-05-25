"""empty message

Revision ID: 6a5ceee87da7
Revises: a570181e3b89
Create Date: 2019-05-25 09:13:12.462051

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6a5ceee87da7'
down_revision = 'a570181e3b89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_route',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('service', sa.Text(), nullable=True),
    sa.Column('route', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['route'], ['route.number'], ),
    sa.ForeignKeyConstraint(['service'], ['service.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('route_price_service')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('route_price_service',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('service', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('route', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['route'], ['route.number'], name='route_price_service_route_fkey'),
    sa.ForeignKeyConstraint(['service'], ['service.name'], name='route_price_service_service_fkey'),
    sa.PrimaryKeyConstraint('id', name='route_price_service_pkey')
    )
    op.drop_table('service_route')
    # ### end Alembic commands ###
