import os
import logging
import sys
from flask import Flask
from dotenv import load_dotenv
from print_api.config import config
from print_api.common.routing import custom_response
from print_api.extensions import migrate, mail, bootstrap, api, cors, jwt
from print_api.models import db

# Resources
from print_api.resources.api_routes import (
    auth_route,
    maintenance_route,
    other_routes,
    print_job_route,
    printer_route,
    user_route,
    role_permission_management_route,
    file_upload_route,
)

load_dotenv("../.env")


def create_app(config_name: str = "development"):
    """
    Create application factory
    :param obj config_name: The configuration name to use.
    :return app: The newly created application
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
    configure_logger(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    """
    Register Flask extensions.
    :param app: the flask application
    """
    api.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    cors.init_app(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
    jwt.init_app(app)
    return None


def register_blueprints(app):
    """
    Register Flask blueprints.
    :param app: the flask application
    """
    api_prefix = app.config["API_PREFIX"]
    app.register_blueprint(user_route.user_api, url_prefix=f"{api_prefix}/users")
    app.register_blueprint(
        printer_route.printer_api, url_prefix=f"{api_prefix}/printers"
    )
    app.register_blueprint(
        maintenance_route.maintenance_api, url_prefix=f"{api_prefix}/maintenance"
    )
    app.register_blueprint(
        print_job_route.print_job_api, url_prefix=f"{api_prefix}/jobs"
    )
    app.register_blueprint(other_routes.other_api, url_prefix=f"{api_prefix}/misc")
    app.register_blueprint(auth_route.auth_api, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(role_permission_management_route.role_permission_api, url_prefix=f"{api_prefix}/permission_management")
    app.register_blueprint(file_upload_route.file_upload_api, url_prefix=f"{api_prefix}/file_upload")
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        error_description = error.description

        # Check if the error is access denied error
        if error_code == 401:
            error_message = "Access denied. You do not have the required permissions to access this resource."
        elif error_code == 404:
            error_message = "Resource not found."
        elif error_code == 413:
            error_message = "The request entity is too large."
        elif error_code == 500:
            error_message = "Internal server error."
        else:
            error_message = "An unknown error occurred."

        return custom_response(error_code, error_message, extra_info=error_description)

    for errcode in [401, 404, 413, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def configure_logger(app):
    """
    Configure the logger
    """
    handler = logging.StreamHandler(sys.stdout)
    logging.getLogger("flask_cors").level = logging.DEBUG
    if not app.logger.handlers:
        app.logger.addHandler(handler)
    return None
