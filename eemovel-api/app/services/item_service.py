from geoalchemy2.functions import ST_DWithin, ST_MakePoint
from geoalchemy2.elements import WKTElement

def buscar_por_raio(lat, lng, raio_metros):
    ponto = ST_MakePoint(lng, lat) 
    return Item.query.filter(
        ST_DWithin(Item.localizacao, ponto, raio_metros)
    ).all()