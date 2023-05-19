import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_limiter.util import get_remote_address

from print_api.config import load_config
from print_api.common.routing import custom_response
from print_api.extensions import migrate, mail, bootstrap, api, cors, jwt, limiter
from print_api.models import db
from print_api.cli import register_commands
from print_api.common import tasks
from print_api.common.tasks import celery
from typing import Union
from celery import Celery as CeleryType

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

logger = logging.getLogger()


def create_app(config_env: str = "development") -> Flask:
    result = entrypoint(config_env=config_env, mode='app')
    assert isinstance(result, Flask), f'Expected a Flask instance, got {type(result)}'
    return result


def create_celery(config_env: str = "development") -> CeleryType:
    result = entrypoint(config_env=config_env, mode='celery')
    assert isinstance(result, CeleryType), f'Expected a Celery instance, got {type(result)}'
    return result


def entrypoint(config_env: str = "development", mode: str = 'app') -> Union[Flask, CeleryType]:
    assert isinstance(mode, str), 'bad mode type "{}"'.format(type(mode))
    assert mode in ('app', 'celery'), 'bad mode "{}"'.format(mode)

    app = Flask(__name__)

    configure_app(app, config_env)
    configure_logging(app, config_env)
    configure_celery(app, tasks.celery)

    # register blueprints
    register_blueprints(app)

    # register commands
    register_commands(app)

    # register extensions
    register_extensions(app)
    # register error handler
    register_errorhandler(app)
    if mode == 'app':
        return app
    elif mode == 'celery':
        return celery


def configure_app(app, config_env: str = "development"):
    conf = load_config(config_env)
    app.config.from_object(conf)


def configure_celery(app, celery):
    # set broker url and result backend from app config
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']

    # subclass task base for app context
    # http://flask.pocoo.org/docs/0.12/patterns/celery/
    task_base = celery.Task

    class AppContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)

    celery.Task = AppContextTask

    # run finalize to process decorated tasks
    celery.finalize()


def register_blueprints(app):
    """
    Register Flask blueprints.
    :param app: the flask application
    """
    api_prefix = os.getenv("API_PREFIX")
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
    app.register_blueprint(role_permission_management_route.role_permission_api,
                           url_prefix=f"{api_prefix}/permission_management")
    app.register_blueprint(file_upload_route.file_upload_api, url_prefix=f"{api_prefix}/file_upload")
    return None


def register_errorhandler(app):
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
        elif error_code == 429:
            error_message = "Too many requests."
        elif error_code == 500:
            error_message = "Internal server error."
        else:
            error_message = "An unknown error occurred."

        return custom_response(error_code, error_message, extra_info=error_description)

    for errcode in [401, 404, 413, 429, 500]:
        app.errorhandler(errcode)(render_error)
    return None


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
    limiter.init_app(app)
    return None


def configure_logging(app, env: str = "development"):
    """
    Configure the logger
    """
    log_location = app.config["LOG_LOCATION"]
    max_log_size = app.config["LOG_MAX_SIZE"]

    if app.config['LOG_TO_STDOUT'] == "True":
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists(log_location):
            os.mkdir(log_location)
        file_handler = RotatingFileHandler(f'{log_location}/{env}.log',
                                           maxBytes=max_log_size, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Print-API Startup')
    app.logger.info(f'Environment: {env}')
    app.logger.info(f'Connected to database: {app.config["SQLALCHEMY_DATABASE_URI"]})')
    return None
