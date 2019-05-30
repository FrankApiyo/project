"""empty message

Revision ID: 9b61258e48cc
Revises: 915efad0c32f
Create Date: 2019-05-27 11:14:20.075784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b61258e48cc'
down_revision = '915efad0c32f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('matatu_routes', sa.Column('route_number', sa.Integer(), nullable=True))
    op.drop_constraint('matatu_routes_route_id_fkey', 'matatu_routes', type_='foreignkey')
    op.create_foreign_key(None, 'matatu_routes', 'route', ['route_number'], ['number'])
    op.drop_column('matatu_routes', 'route_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('matatu_routes', sa.Column('route_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'matatu_routes', type_='foreignkey')
    op.create_foreign_key('matatu_routes_route_id_fkey', 'matatu_routes', 'route', ['route_id'], ['number'])
    op.drop_column('matatu_routes', 'route_number')
    # ### end Alembic commands ###