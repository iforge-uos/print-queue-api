from flask import Flask, Blueprint
from flask_restful import Api, Resource, url_for
from resources.foo import Foo
from resources.bar import Bar

app = Flask(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)
app.register_blueprint(api_bp)

api.add_resource(Foo, '/Foo', '/Foo/<string:id>')
api.add_resource(Bar, '/Bar', '/Bar/<string:id>')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)