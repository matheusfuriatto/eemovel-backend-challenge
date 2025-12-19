import math

def calculate_distance(p1, p2):
    """Distância Euclidiana simples (pode ser substituída por Haversine)"""
    return math.sqrt((p1['lat'] - p2['lat'])**2 + (p1['lon'] - p2['lon'])**2)

def optimize_route(start_point, destinations):
    """
    Algoritmo Vizinho Mais Próximo (Nearest Neighbor).
    Não garante a solução perfeita, mas é muito rápido e eficiente para rotas de entrega.
    """
    route = [start_point]
    current = start_point
    unvisited = destinations.copy()

    while unvisited:
        nearest = None
        min_dist = float('inf')

        for point in unvisited:
            dist = calculate_distance(current, point)
            if dist < min_dist:
                min_dist = dist
                nearest = point

        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    return route