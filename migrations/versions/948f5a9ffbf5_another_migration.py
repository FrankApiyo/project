"""another migration

Revision ID: 948f5a9ffbf5
Revises: 
Create Date: 2019-05-14 18:27:57.597411

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '948f5a9ffbf5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
   pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('route', 'to_location',
               existing_type=sa.Text(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('route', 'from_location',
               existing_type=sa.Text(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
