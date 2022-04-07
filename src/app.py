import os
from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_restful import Api
from dotenv import load_dotenv
from config import app_config
from common.errors import errors

from extensions import (
    db,
    migrate,
    mail,
    bootstrap
)
# Resources
from resources import user_route, printer_route, print_job_route, maintenance_route, other_routes, auth_routes, user_views

load_dotenv("../.env")


def create_app(config_object=app_config[os.getenv('FLASK_ENV')]):
    """
    Create application factory
    :param obj config_object: The configuration object to use.
    :return app: The newly created application
    """
    app = Flask(__name__.split(".")[0])
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp, errors=errors)
    app.register_blueprint(api_bp)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    """
    Register Flask extensions.
    :param app: the flask application
    """
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    return None


def register_blueprints(app):
    """
    Register Flask blueprints.
    :param app: the flask application
    """
    api_prefix = app.config['API_PREFIX']
    app.register_blueprint(
        user_route.user_api,
        url_prefix=f'{api_prefix}/users')
    app.register_blueprint(
        printer_route.printer_api,
        url_prefix=f'{api_prefix}/printers')
    app.register_blueprint(
        maintenance_route.maintenance_api,
        url_prefix=f'{api_prefix}/maintenance')
    app.register_blueprint(
        print_job_route.print_job_api,
        url_prefix=f'{api_prefix}/queue')
    app.register_blueprint(
        other_routes.other_api,
        url_prefix=f'{api_prefix}/misc')
    app.register_blueprint(
        auth_routes.auth_api,
        url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(
        user_views.user_view,
        url_prefix='/')
    return None


def register_errorhandlers(app):
    """
    Register error handlers.
    :param app: the flask application
    """
    # TODO IMPLEMENT
    return None


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=app.config['PORT'])
