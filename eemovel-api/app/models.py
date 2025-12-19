from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    # SRID 4326 é o padrão WGS84 (lat/long)
    localizacao = db.Column(Geometry(geometry_type='POINT', srid=4326))

    def to_dict(self):
        point = to_shape(self.localizacao)
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "latitude": point.y,
            "longitude": point.x
        }