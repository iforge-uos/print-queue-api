import os
from flask import Flask, Blueprint, Response
from flask_restful import Api
from flask_migrate import Migrate
from flask_mail import Mail, Message
from dotenv import load_dotenv
from models import db
from common import mail
from config import app_config

# Resources
from resources.user_route import user_api as user_blueprint
from resources.printer_route import printer_api as printer_blueprint
from resources.maintenance_route import maintenance_api as maintenance_blueprint
from resources.print_job_route import print_job_api as printjobs_blueprint

# TODO REWRITE THIS AS AN APPLICATION FACTORY MAYBE?

API_PREFIX = "/api/v1"

load_dotenv("../.env")

env_name = os.getenv('FLASK_ENV')
port = os.getenv('PORT')


app = Flask(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)
app.register_blueprint(api_bp)

app.config.from_object(app_config[env_name])

db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)


app.register_blueprint(user_blueprint, url_prefix=f'{API_PREFIX}/users')
app.register_blueprint(printer_blueprint, url_prefix=f'{API_PREFIX}/printers')
app.register_blueprint(maintenance_blueprint,
                       url_prefix=f'{API_PREFIX}/maintenance')
app.register_blueprint(printjobs_blueprint, url_prefix=f'{API_PREFIX}/queue')


@app.route('/', methods=["GET"])
def index():
    '''
    Test Endpoint
    '''
    msg = Message('Testing Email', sender='sam@mailtrap.io',
                  recipients=['test@mailtrap.io'])
    msg.body = "Email has been tested"
    mail.send(msg)
    return Response(
        mimetype="application/text",
        response="sweet cheeks",
        status=418
    )


@app.route('/government-secrets', methods=["GET"])
def index_2():
    '''
    Test Endpoint
    '''
    return Response(
        mimetype="application/text",
        response="uh oh",
        status=451
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
