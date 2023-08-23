from flask_sqlalchemy import SQLAlchemy

# initialize our db
db = SQLAlchemy()

from .user_role import UserRole
from .user import User, user_schema
from .role_permission import RolePermission
from .role import Role
from .permission import Permission
from .printers import Printer, printer_schema, printer_type, printer_location
from .maintenance_logs import MaintenanceLog, maintenance_schema
from .blacklisted_tokens import BlacklistedToken
from .print_jobs import PrintJob, print_job_schema
