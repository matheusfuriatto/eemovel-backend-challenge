from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db

auth_ns = Namespace('auth', description='Autenticação')

user_model = auth_ns.model('User', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.json
        if User.query.filter_by(email=data['email']).first():
            return {"message": "Usuário já existe"}, 400
        
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
            # CORREÇÃO AQUI: Convertendo explicitamente o ID para string
            # Isso evita o erro 422 "Subject must be a string"
            token = create_access_token(identity=str(user.id))
            
            return {"access_token": token}, 200
            
        return {"message": "Credenciais inválidas"}, 401