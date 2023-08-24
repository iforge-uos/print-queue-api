from flask_sqlalchemy import SQLAlchemy

# initialize our db
db = SQLAlchemy()

from .user_role import UserRole
from .user import User, UserSchema
from .role_permission import RolePermission
from .role import Role
from .permission import Permission
from .printers import Printer, PrinterSchema, PrinterType, PrinterLocation
from .maintenance_logs import MaintenanceLog, MaintenanceSchema
from .blacklisted_tokens import BlacklistedToken
from .print_jobs import PrintJob, PrintJobSchema
