from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from app.models import db, User, Item
from geoalchemy2.functions import ST_Distance_Sphere, ST_MakePoint
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
jwt = JWTManager(app)

# Configuração de Segurança para o Swagger
authorizations = {
    'apikey': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}
}
api = Api(app, version='1.0', title='GeoItems API', authorizations=authorizations, security='apikey')

# Namespaces
auth_ns = api.namespace('auth', description='Autenticação')
item_ns = api.namespace('items', description='Operações Geográficas')

# Modelos do Swagger
item_model = api.model('Item', {
    'nome': fields.String(required=True),
    'descricao': fields.String(),
    'lat': fields.Float(required=True),
    'lng': fields.Float(required=True)
})

user_model = api.model('User', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.json
        user = User(email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return {"message": "Usuário criado"}, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            token = create_access_token(identity=user.id)
            return {"access_token": f"Bearer {token}"}, 200
        return {"message": "Credenciais inválidas"}, 401

@item_ns.route('/')
class ItemList(Resource):
    def get(self):
        """Busca por raio: /items/?lat=-23.5&lng=-46.6&radius=5000"""
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', type=float)

        if all([lat, lng, radius]):
            ponto = ST_MakePoint(lng, lat)
            itens = Item.query.filter(ST_Distance_Sphere(Item.localizacao, ponto) <= radius).all()
        else:
            itens = Item.query.all()
        return [i.to_dict() for i in itens]

    @jwt_required()
    @item_ns.expect(item_model)
    def post(self):
        data = request.json
        ponto = f'SRID=4326;POINT({data["lng"]} {data["lat"]})'
        novo_item = Item(nome=data['nome'], descricao=data['descricao'], localizacao=ponto)
        db.session.add(novo_item)
        db.session.commit()
        return novo_item.to_dict(), 201