"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_cors import CORS

from print_api.common.routing import custom_response

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bootstrap = Bootstrap()
api = Api()
cors = CORS()
jwt = JWTManager()


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    error_message = "Token has expired"
    error_details = {"message": error_message}
    return custom_response(status_code=401, details=error_message, extra_info=error_details)
