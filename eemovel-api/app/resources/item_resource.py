from flask import request
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required
from app.models.item import Item
from app import db
from geoalchemy2.functions import ST_Distance_Sphere, ST_MakePoint

item_ns = Namespace('items', description='Operações de Itens')

@item_ns.route('/')
class ItemList(Resource):
    @item_ns.doc('list_items')
    def get(self):
        """Busca itens com filtro opcional de raio (lat, lng, radius)"""
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', type=float) # em metros

        if lat and lng and radius:
            # Busca geoespacial eficiente
            ponto_ref = ST_MakePoint(lng, lat)
            items = Item.query.filter(
                ST_Distance_Sphere(Item.localizacao, ponto_ref) <= radius
            ).all()
            return [it.to_dict() for it in items]
        
        return [it.to_dict() for it in Item.query.all()]

    @item_ns.expect(item_model) # O modelo definido no passo anterior
    @jwt_required()
    def post(self):
        """Cria item (Requer JWT)"""
        # Lógica de salvar com WKTElement para o PostGIS
        pass