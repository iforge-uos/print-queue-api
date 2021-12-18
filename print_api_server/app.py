from flask import Flask, Blueprint
from flask_restful import Api, Resource, url_for
from resources.foo import Foo
from resources.bar import Bar
from models import db

app = Flask(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)
app.register_blueprint(api_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = ""
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


api.add_resource(Foo, '/Foo', '/Foo/<string:id>')
api.add_resource(Bar, '/Bar', '/Bar/<string:id>')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)