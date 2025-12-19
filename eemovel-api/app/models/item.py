from app.extensions import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    descricao = db.Column(db.Text)
    localizacao = db.Column(Geometry(geometry_type='POINT', srid=4326))

    def to_dict(self):
        point = to_shape(self.localizacao)
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'latitude': point.y,
            'longitude': point.x
        }