from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.models.item import Item
from app.extensions import db
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from sqlalchemy import cast
import logging

item_ns = Namespace('items', description='Operações Geoespaciais e Logística', security='apikey')

# Modelo para documentação Swagger
item_model = item_ns.model('Item', {
    'nome': fields.String(required=True, example='Ponto A'),
    'descricao': fields.String(example='Descrição do Ponto'),
    'latitude': fields.Float(required=True, example=-24.9554),
    'longitude': fields.Float(required=True, example=-53.4552)
})

@item_ns.route('/')
class ItemList(Resource):
    @jwt_required()
    @item_ns.doc(
        responses={200: 'Sucesso', 400: 'Erro de validação'},
        params={
            'lat': {'description': 'Latitude central para a busca', 'type': 'float', 'example': -24.9554},
            'lng': {'description': 'Longitude central para a busca', 'type': 'float', 'example': -53.4552},
            'radius': {'description': 'Raio de busca em metros', 'type': 'float', 'example': 5000}
        }
    )
    def get(self):
        """Lista itens com busca geoespacial opcional por raio"""
        try:
            # Captura os parâmetros da URL
            lat = request.args.get('lat', type=float)
            lng = request.args.get('lng', type=float)
            radius = request.args.get('radius', type=float)
            
            query = Item.query
            # Só aplica o filtro se os TRÊS parâmetros forem enviados
            if all(v is not None for v in [lat, lng, radius]):
                query = query.filter(
                    db.func.ST_DWithin(
                        cast(Item.localizacao, Geography),
                        db.func.ST_MakePoint(lng, lat),
                        radius
                    )
                )
            
            itens = query.all()
            return [i.to_dict() for i in itens], 200
            
        except Exception as e:
            return {"message": "Erro ao buscar itens", "error": str(e)}, 500

    @item_ns.expect(item_model)
    @jwt_required()
    @item_ns.doc(responses={201: 'Item criado com sucesso', 400: 'Dados inválidos'})
    def post(self):
        """Cria um novo item (Requer JWT)"""
        try:
            data = request.json
            # Validação simples
            if not data.get('nome') or data.get('latitude') is None:
                return {"message": "Campos obrigatórios ausentes"}, 400

            point = f'SRID=4326;POINT({data["longitude"]} {data["latitude"]})'
            new_item = Item(
                nome=data['nome'], 
                descricao=data.get('descricao'), 
                localizacao=point
            )
            db.session.add(new_item)
            db.session.commit()
            
            return {
                "message": "Item criado com sucesso",
                "item": new_item.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao criar item", "error": str(e)}, 500

@item_ns.route('/<int:id>')
@item_ns.param('id', 'O identificador único do item')
class ItemResource(Resource):
    
    @jwt_required()
    @item_ns.expect(item_model) # <-- ADICIONE ESTA LINHA AQUI
    @item_ns.doc(responses={200: 'Item atualizado', 404: 'Item não encontrado', 400: 'Dados inválidos'})
    def put(self, id):
        """Atualiza um item existente (Requer JWT)"""
        try:
            item = Item.query.get(id)
            if not item:
                return {"message": f"Item com ID {id} não encontrado"}, 404

            data = request.json
            if not data:
                return {"message": "Nenhum dado enviado para atualização"}, 400

            item.nome = data.get('nome', item.nome)
            item.descricao = data.get('descricao', item.descricao)
            
            if 'latitude' in data and 'longitude' in data:
                item.localizacao = f'SRID=4326;POINT({data["longitude"]} {data["latitude"]})'
                
            db.session.commit()
            return {
                "message": "Item atualizado com sucesso",
                "item": item.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao atualizar item", "error": str(e)}, 500
    @jwt_required()
    @item_ns.doc(responses={200: 'Item removido', 404: 'Item não encontrado'})
    def delete(self, id):
        """Remove um item (Requer JWT)"""
        try:
            item = Item.query.get(id)
            if not item:
                return {"message": f"Erro: Item {id} não existe no banco de dados"}, 404
            
            db.session.delete(item)
            db.session.commit()
            
            # Alterado de 204 para 200 para que o corpo da mensagem apareça
            return {
                "status": "sucesso",
                "message": f"O item '{item.nome}' (ID: {id}) foi removido permanentemente."
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao deletar item", "error": str(e)}, 500

@item_ns.route('/optimize')
class OptimizeRoute(Resource):
    @jwt_required()
    @item_ns.doc(security='apikey')
    def get(self):
        """Algoritmo de Vizinho Mais Próximo para Logística (Requer JWT)"""
        try:
            capacity = request.args.get('capacity', type=int, default=3)
            items_db = Item.query.all()
            
            # Inicializamos a variável aqui para evitar o erro "not defined"
            all_trips = []
            
            if not items_db:
                return {
                    'message': 'Nenhum item encontrado no banco para otimização',
                    'resumo': {'total_itens': 0, 'viagens_geradas': 0},
                    'trips': []
                }, 200

            # Prepara a lista de itens não visitados
            unvisited = []
            for item in items_db:
                unvisited.append({
                    'data': item.to_dict(),
                    'geom': to_shape(item.localizacao)
                })
            
            # Algoritmo de Otimização (Vizinho mais próximo)
            while unvisited:
                current_trip = []
                # Pega o primeiro item disponível para começar a viagem
                current = unvisited.pop(0)
                current_trip.append(current['data'])
                
                while len(current_trip) < capacity and unvisited:
                    # Busca o item mais próximo do ponto atual
                    closest_node = min(
                        unvisited, 
                        key=lambda x: current['geom'].distance(x['geom'])
                    )
                    unvisited.remove(closest_node)
                    current_trip.append(closest_node['data'])
                    current = closest_node
                
                all_trips.append(current_trip)

            return {
                'status': 'sucesso',
                'resumo': {
                    'total_itens': len(items_db),
                    'capacidade': capacity,
                    'viagens_geradas': len(all_trips)
                },
                'trips': all_trips
            }, 200

        except Exception as e:
            # Log do erro no console para facilitar o debug
            print(f"Erro detalhado na otimização: {str(e)}")
            return {
                "message": "Erro no algoritmo de otimização",
                "error": str(e)
            }, 500