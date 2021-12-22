"""empty message

Revision ID: 23ecf9960552
Revises: 374004cb5621
Create Date: 2021-12-22 02:27:46.494573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23ecf9960552'
down_revision = '374004cb5621'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('maintenance_logs', 'printer_ID',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('maintenance_logs', 'printer_ID',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###