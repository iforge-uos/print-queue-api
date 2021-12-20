"""empty message

Revision ID: e1b6346d33dc
Revises: 0964ebc498e7
Create Date: 2021-12-20 11:01:07.563928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1b6346d33dc'
down_revision = '0964ebc498e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('printers', sa.Column('total_time_printed', sa.Integer(), nullable=True))
    op.drop_column('printers', 'total_timed_printed')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('printers', sa.Column('total_timed_printed', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('printers', 'total_time_printed')
    # ### end Alembic commands ###
