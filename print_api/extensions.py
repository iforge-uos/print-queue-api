"""Extensions module. Each extension is initialized in the app factory located in entrypoint_api.py."""
import os
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from print_api.common.routing import custom_response

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bootstrap = Bootstrap()
api = Api()
cors = CORS()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    strategy='fixed-window',
    storage_uri=os.environ.get('RATELIMIT_STORAGE_URL'),
    default_limits=[
        "200 per day",
        "50 per hour",
        "10 per minute",
        "1 per second",
    ],
)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    error_message = "Token has expired"
    error_details = {"message": error_message}
    return custom_response(status_code=401, details=error_message, extra_info=error_details)
