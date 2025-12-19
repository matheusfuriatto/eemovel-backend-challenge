from flask import Flask
from flask_restx import Api
from .extensions import db, bcrypt, jwt
from .config import Config
from .namespaces.item_ns import item_ns
from .namespaces.auth_ns import auth_ns

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        }
    }

    api = Api(app, 
              title='Eemovel API', 
              version='1.0', 
              description='API de Logística Inteligente',
              authorizations=authorizations, 
              security='Bearer')

    api.add_namespace(item_ns)
    api.add_namespace(auth_ns)

    return app