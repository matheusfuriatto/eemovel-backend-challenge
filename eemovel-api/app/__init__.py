from flask import Flask
from flask_restx import Api
from app.extensions import db, bcrypt, jwt
from app.namespaces.item_ns import item_ns
from app.namespaces.auth_ns import auth_ns

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin_password@db:5432/geodb'
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Boa prática adicionar
    
    # Inicializa extensões
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # 1. CONFIGURAÇÃO DE SEGURANÇA PARA O SWAGGER
    # Isso define como o Swagger deve enviar o token (no Header, como Authorization)
    authorizations = {
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Digite no campo: Bearer <seu_token_jwt>"
        }
    }

    # 2. INICIALIZAÇÃO DA API COM SEGURANÇA
    api = Api(
        app, 
        title='Eemovel Backend API',
        version='1.0',
        description='API para gestão de pontos georreferenciados com Autenticação JWT',
        doc='/docs',
        authorizations=authorizations, # Ativa a definição de segurança
        security='apikey'              # Aplica o cadeado globalmente na interface
    )

    # Registra os Namespaces
    api.add_namespace(item_ns, path='/items')
    api.add_namespace(auth_ns, path='/auth')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)