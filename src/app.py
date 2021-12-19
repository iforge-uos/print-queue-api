import os
from flask import Flask, Blueprint
from flask_restful import Api, Resource, url_for
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db
from resources.user_route import user_api as user_blueprint


# Loading db config
load_dotenv()
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
server_name = os.getenv('DB_HOST')
server_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

app = Flask(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)
app.register_blueprint(api_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{server_name}:{server_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')


@app.route('/', methods=["GET"])
def index():
    '''
    Test Endpoint
    '''
    return "You did good son"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
