"""empty message

Revision ID: 059f8108256b
Revises: 
Create Date: 2022-09-26 00:29:37.306935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '059f8108256b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('date_added', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('associated_version', sa.String(), nullable=True),
    sa.Column('permission_value', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('printers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('printer_name', sa.String(length=50), nullable=False),
    sa.Column('printer_type', sa.Enum('ultimaker', 'prusa', name='printer_type'), nullable=False),
    sa.Column('ip', sa.String(length=15), nullable=True),
    sa.Column('api_key', sa.String(length=50), nullable=True),
    sa.Column('total_time_printed', sa.Integer(), nullable=True),
    sa.Column('completed_prints', sa.Integer(), nullable=True),
    sa.Column('failed_prints', sa.Integer(), nullable=True),
    sa.Column('total_filament_used', sa.Integer(), nullable=True),
    sa.Column('days_on_time', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('printer_name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('user_score', sa.Integer(), nullable=False),
    sa.Column('is_rep', sa.Boolean(), nullable=False),
    sa.Column('score_editable', sa.Boolean(), nullable=True),
    sa.Column('short_name', sa.String(), nullable=True),
    sa.Column('date_added', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('maintenance_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('printer_id', sa.Integer(), nullable=False),
    sa.Column('maintenance_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('maintenance_info', sa.String(), nullable=False),
    sa.Column('done_by', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['printer_id'], ['printers.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('print_jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_queued', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('print_name', sa.String(length=60), nullable=False),
    sa.Column('gcode_slug', sa.String(), nullable=False),
    sa.Column('stl_slug', sa.String(), nullable=True),
    sa.Column('date_added', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('date_started', sa.DateTime(timezone=True), nullable=True),
    sa.Column('date_ended', sa.DateTime(timezone=True), nullable=True),
    sa.Column('colour', sa.String(), nullable=True),
    sa.Column('upload_notes', sa.String(), nullable=True),
    sa.Column('queue_notes', sa.String(), nullable=True),
    sa.Column('checked_by', sa.Integer(), nullable=True),
    sa.Column('printer', sa.Integer(), nullable=True),
    sa.Column('printer_type', sa.Enum('ultimaker', 'prusa', name='printer_type'), nullable=False),
    sa.Column('project', sa.Enum('personal', 'uni_module', 'co_curricular', 'society', 'other', name='project_types'), nullable=False),
    sa.Column('project_string', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('queued', 'approval', 'running', 'complete', 'failed', 'rejected', 'under_review', name='job_status'), nullable=False),
    sa.Column('print_time', sa.Integer(), nullable=True),
    sa.Column('filament_usage', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['checked_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['printer'], ['printers.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('print_jobs')
    op.drop_table('maintenance_logs')
    op.drop_table('users')
    op.drop_table('printers')
    op.drop_table('auth')
    # ### end Alembic commands ###
