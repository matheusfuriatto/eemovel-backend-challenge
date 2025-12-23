from flask import Flask
from flask_restx import Api
from app.extensions import db, bcrypt, jwt
from app.namespaces.item_ns import item_ns
from app.namespaces.auth_ns import auth_ns

def create_app():
    app = Flask(__name__)
    
    # Configurações (ajuste conforme seu environment)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin_password@db:5432/geodb'
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'
    
    # Inicializa extensões
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Configuração do Flask-RESTx para documentação em /docs
    api = Api(
        app, 
        title='Eemovel Backend API',
        version='1.0',
        description='API para gestão de pontos georreferenciados',
        doc='/docs' # <-- Aqui define a rota da documentação
    )

    # Registra os Namespaces
    api.add_namespace(item_ns, path='/items')
    api.add_namespace(auth_ns, path='/auth')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)