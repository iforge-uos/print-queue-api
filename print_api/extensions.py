"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bootstrap = Bootstrap()
api = Api()
cors = CORS()
jwt = JWTManager()