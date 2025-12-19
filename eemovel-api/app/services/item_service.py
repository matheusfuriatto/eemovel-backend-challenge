from geoalchemy2.functions import ST_DWithin, ST_MakePoint
from geoalchemy2.elements import WKTElement

def buscar_por_raio(lat, lng, raio_metros):
    # Ponto central para a busca
    ponto = ST_MakePoint(lng, lat) 
    # Filtra itens dentro do raio usando o índice espacial do PostGIS
    return Item.query.filter(
        ST_DWithin(Item.localizacao, ponto, raio_metros)
    ).all()