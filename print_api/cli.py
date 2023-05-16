import click
import urllib.parse
from tabulate import tabulate
from datetime import datetime, timedelta
from print_api.models import db, Role, Permission, RolePermission, BlacklistedToken, Printer, printer_type, \
    printer_location
from print_api.config import Config


def register_commands(app):
    @app.cli.command("seed-default-printers")
    def meta_seed_default_printers():
        """Seed the database with default printer data."""
        seed_default_printers()

    @app.cli.command("seed-default-authorisation")
    def meta_seed_default_auth():
        """Seed the database with default authorisation data."""
        seed_default_auth()

    @app.cli.command("seed-db")
    def meta_seed_all():
        seed_all()

    @app.cli.command("nuke-db")
    def db_go_boom():
        """Drop and re-initialise the database."""
        click.echo(click.style("Nuking the database!", fg="red", bold=True))
        drop_db()
        init_db()
        seed_all()

    @app.cli.command("list-routes")
    def list_routes():
        """List all routes."""
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            line = urllib.parse.unquote("{}\t{}\t{}".format(rule.endpoint, methods, rule))  # replace spaces with tabs
            output.append(line)

        click.echo(click.style("Routes:", fg="green", bold=True))
        for line in sorted(output):
            endpoint, methods, rule = line.split('\t')  # split by tabs
            click.echo(
                f"{click.style(endpoint, fg='yellow')}\t"
                f"{click.style(methods, fg='blue')}\t"
                f"{click.style(rule, fg='cyan')}"
            )

    @app.cli.command("drop-db")
    def meta_drop_db():
        drop_db()

    @app.cli.command("init-db")
    def meta_init_db():
        init_db()

    @app.cli.command("clear-expired-blacklist")
    def clear_expired_blacklist():
        """Clear blacklisted tokens that have been expired for longer than the refresh token expiry time."""
        expiry_date = datetime.utcnow() - timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES)

        if click.confirm(click.style('Are you sure you want to clear all blacklisted tokens older than the refresh '
                                     'token expiry time?', fg="red"), abort=True):
            num_deleted = db.session.query(BlacklistedToken).filter(
                BlacklistedToken.blacklisted_at <= expiry_date).delete()
            db.session.commit()
            click.echo(click.style(f"Cleared {num_deleted} expired blacklisted tokens.", fg="green"))

    @app.cli.command("clear-all-blacklist")
    def clear_all_blacklist():
        """Clear all blacklisted tokens."""
        if click.confirm(click.style('Are you sure you want to clear all blacklisted tokens?', fg="red"), abort=True):
            num_deleted = db.session.query(BlacklistedToken).delete()
            db.session.commit()
            click.echo(click.style(f"Cleared {num_deleted} blacklisted tokens.", fg="green"))


def seed_default_printers():
    """Seed the database with default printers."""
    printer_data = [
        {"printer_name": "Bernoulli", "printer_type": printer_type.prusa, "location": printer_location.diamond,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
        {"printer_name": "Brunel", "printer_type": printer_type.prusa, "location": printer_location.diamond,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
        {"printer_name": "Curie", "printer_type": printer_type.prusa, "location": printer_location.diamond,
         "ip": "", "api_key": "",
         "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0, "total_filament_used": 0,
         "days_on_time": 0},
        {"printer_name": "Lamarr", "printer_type": printer_type.prusa, "location": printer_location.diamond,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
        {"printer_name": "Lovelace", "printer_type": printer_type.prusa, "location": printer_location.heartspace,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
        {"printer_name": "Turing", "printer_type": printer_type.prusa, "location": printer_location.heartspace,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
        {"printer_name": "Hawking", "printer_type": printer_type.prusa, "location": printer_location.heartspace,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
        {"printer_name": "Tesla", "printer_type": printer_type.prusa, "location": printer_location.heartspace,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
        {"printer_name": "Da Vinci", "printer_type": printer_type.prusa, "location": printer_location.heartspace,
         "ip": "",
         "api_key": "", "total_time_printed": 0, "completed_prints": 0, "failed_prints": 0,
         "total_filament_used": 0, "days_on_time": 0},
    ]

    if Printer.query.count() > 0:
        return False

    for printer in printer_data:
        click.echo(click.style("Seeding printer: " + printer["printer_name"], italic=True))
        db.session.add(Printer(printer))
    db.session.commit()

    return True


def seed_default_auth():
    """Seed the database with default user and roles."""

    if Role.query.count() > 0:
        return False

    # Create the permissions
    permissions_user = [
        Permission(name="view_user_self", description="View own user data"),
        Permission(name="view_user_any", description="View any user data"),
        Permission(name="create_user", description="Create new users"),
        Permission(name="edit_user", description="Edit user data"),
        Permission(name="delete_user", description="Delete users"),
    ]

    permissions_printer = [
        Permission(name="view_printer_any", description="View any printer data"),
        Permission(name="create_printer", description="Create new printers"),
        Permission(name="edit_printer", description="Edit printer data"),
        Permission(name="delete_printer", description="Delete printers"),
    ]

    permissions_print_job = [
        Permission(name="view_print_job_any", description="View any print job data"),
        Permission(name="create_print_job_any", description="Create new print jobs"),
        Permission(name="edit_print_job_any", description="Edit print job data"),
        Permission(name="delete_print_job_any", description="Delete print jobs"),
        Permission(name="view_print_job_self", description="View own print job data"),
        Permission(name="create_print_job_self", description="Create own new print jobs"),
        Permission(name="edit_print_job_self", description="Edit own print job data"),
        Permission(name="delete_print_job_self", description="Delete own print jobs"),
        Permission(name="start_print_job", description="Start print jobs"),
        Permission(name="cancel_print_job", description="Cancel print jobs"),
        Permission(name="accept_print_job", description="Accept print jobs"),
        Permission(name="reject_print_job", description="Reject print jobs"),
    ]

    permissions_files = [
        Permission(name="upload_model_file", description="Upload model files stl etc."),
        Permission(name="upload_print_file", description="Upload print files gcode etc."),
    ]

    permissions_roles_and_auth = [
        Permission(name="view_role", description="View role data"),
        Permission(name="create_role", description="Create new roles"),
        Permission(name="edit_role", description="Edit role data"),
        Permission(name="delete_role", description="Delete roles"),
        Permission(name="view_permission", description="View permission data"),
        Permission(name="create_permission", description="Create new permissions"),
        Permission(name="edit_permission", description="Edit permission data"),
        Permission(name="delete_permission", description="Delete permissions"),
        Permission(name="assign_role", description="Assign roles to users"),
        Permission(name="assign_permission", description="Assign permissions to roles"),
        Permission(name="remove_permission", description="Remove permissions from roles"),
        Permission(name="remove_role", description="Remove roles from users"),
    ]

    permissions = permissions_user + permissions_printer + permissions_print_job + permissions_files \
                  + permissions_roles_and_auth

    # Add the permissions to the session
    db.session.add_all(permissions)

    # Create the roles
    roles = [
        Role(name="default"),
        Role(name="root"),
    ]

    # Add the roles to the session
    db.session.add_all(roles)

    # Flush the session to populate ids
    db.session.flush()

    # Assign limited permissions to the default role
    default_role = Role.query.filter_by(name="default").first()
    view_permission = Permission.query.filter_by(name="view_user_self").first()
    db.session.add(RolePermission(role_id=default_role.id, permission_id=view_permission.id))

    # Assign all permissions to the root role
    root_role = Role.query.filter_by(name="root").first()
    for permission in permissions:
        db.session.add(RolePermission(role_id=root_role.id, permission_id=permission.id))

    # Commit the session
    db.session.commit()

    return True


def drop_db():
    """Drop the database."""
    db.drop_all()
    click.echo(click.style("Dropped the database.", fg="red"))


def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo(click.style("Initialized the database.", fg="green"))


def seed_all():
    """Seed the database with default data """
    click.echo(click.style("Begin Seeding!", fg="green", bold=True))

    for seed_name, seed_func in SEED_FUNCTIONS.items():
        if seed_func():
            click.echo(click.style(f"Successfully seeded {seed_name}", italic=True, fg="green"))
        else:
            click.echo(click.style(f"{seed_name} already seeded", fg="yellow", italic=True))

    click.echo(click.style("Seeding Complete!", fg="green", bold=True))


SEED_FUNCTIONS = {
    'Auth': seed_default_auth,
    'Printers': seed_default_printers,
}
