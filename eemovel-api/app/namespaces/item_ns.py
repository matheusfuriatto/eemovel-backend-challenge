from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.models.item import Item
from app.extensions import db
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from sqlalchemy import cast

item_ns = Namespace('items', description='Operações Geoespaciais e Logística')

# Modelo para documentação Swagger
item_model = item_ns.model('Item', {
    'nome': fields.String(required=True, example='Ponto A'),
    'descricao': fields.String(example='Descrição do Ponto'),
    'latitude': fields.Float(required=True, example=-24.9554),
    'longitude': fields.Float(required=True, example=-53.4552)
})

@item_ns.route('/')
class ItemList(Resource):
    def get(self):
        """Lista itens com busca geoespacial opcional por raio"""
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', type=float)
        
        query = Item.query
        if all([lat is not None, lng is not None, radius is not None]):
            query = query.filter(
                db.func.ST_DWithin(
                    cast(Item.localizacao, Geography),
                    db.func.ST_MakePoint(lng, lat),
                    radius
                )
            )
        return [i.to_dict() for i in query.all()], 200

    @item_ns.expect(item_model)
    @jwt_required()
    def post(self):
        """Cria um novo item (Requer JWT)"""
        data = request.json
        point = f'SRID=4326;POINT({data["longitude"]} {data["latitude"]})'
        new_item = Item(
            nome=data['nome'], 
            descricao=data.get('descricao'), 
            localizacao=point
        )
        db.session.add(new_item)
        db.session.commit()
        return new_item.to_dict(), 201

@item_ns.route('/<int:id>')
@item_ns.param('id', 'O identificador único do item')
class ItemResource(Resource):
    @jwt_required()
    def put(self, id):
        """Atualiza um item existente (Requer JWT)"""
        data = request.json
        item = Item.query.get_or_404(id)
        
        item.nome = data.get('nome', item.nome)
        item.descricao = data.get('descricao', item.descricao)
        
        if 'latitude' in data and 'longitude' in data:
            item.localizacao = f'SRID=4326;POINT({data["longitude"]} {data["latitude"]})'
            
        db.session.commit()
        return item.to_dict(), 200

    @jwt_required()
    def delete(self, id):
        """Remove um item (Requer JWT)"""
        item = Item.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item removido com sucesso"}, 204

@item_ns.route('/optimize')
class OptimizeRoute(Resource):
    @jwt_required()
    def get(self):
        """Algoritmo de Vizinho Mais Próximo para Logística (Requer JWT)"""
        capacity = request.args.get('capacity', type=int, default=3)
        items_db = Item.query.all()
        
        if not items_db:
            return {'trips': []}, 200

        unvisited = []
        for item in items_db:
            unvisited.append({
                'data': item.to_dict(),
                'geom': to_shape(item.localizacao)
            })
            
        all_trips = []
        while unvisited:
            current_trip = []
            current = unvisited.pop(0)
            current_trip.append(current['data'])
            
            while len(current_trip) < capacity and unvisited:
                closest_node = min(
                    unvisited, 
                    key=lambda x: current['geom'].distance(x['geom'])
                )
                unvisited.remove(closest_node)
                current_trip.append(closest_node['data'])
                current = closest_node
            
            all_trips.append(current_trip)

        return {
            'resumo': {
                'total_itens': len(items_db),
                'capacidade': capacity,
                'viagens_geradas': len(all_trips)
            },
            'trips': all_trips
        }, 200