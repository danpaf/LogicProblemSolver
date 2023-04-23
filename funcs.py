import datetime
import json
import pprint

import networkx as nx
import requests
import time

from db.models import NodeDBModel, RibDBModel

node = NodeDBModel.select()[0]
rib = RibDBModel.select().where(RibDBModel.from_node==node)
def get_coordinates(city_name):
    formatted_city = city_name
    url = f'https://api.openrouteservice.org/geocode/search?api_key=5b3ce3597851110001cf62482a313763d43c43699380e8b5dc181d5e&text={formatted_city}&boundary.country=RUS&sources=whosonfirst'
    response = requests.get(url)
    result = json.loads(response.content)
    if result and result.get('bbox'):
        lat, lon = result.get('bbox')[0], result.get('bbox')[1]
        print(lat,lon)
        return lat, lon
    else:
        print(f"No coordinates found for {formatted_city} Response{response.text}")
        return None, None

def get_route(from_city, to_city):
    from_coords = get_coordinates(from_city)
    print(from_city,from_coords)
    to_coords = get_coordinates(to_city)
    print(to_coords[1])
    if from_coords is None or to_coords is None:
        return None, None, 'Error: Coordinates not found for one or both cities'

    time.sleep(5)
    url = f'https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf62482a313763d43c43699380e8b5dc181d5e&start={from_coords[0]},{from_coords[1]}&end={to_coords[0]},{to_coords[1]}'
    response = requests.get(url)
    result = json.loads(response.content)
    if 'features' not in result:
        return None, None, 'Error: Route not found'

    distance = result['features'][0]['properties']['segments'][0]['distance']
    duration = result['features'][0]['properties']['segments'][0]['duration']
    print(distance, "дистанция",duration , "время")
    return distance, duration, None

def getRoutes(node,rib):
    G = nx.MultiDiGraph()
    for r in RibDBModel.select():
        city1 = r.from_node.title
        city2 = r.to_node.title
        # duration, distance = funcs.get_route(city1, city2)[:2]
        # time = duration
        weight = r.time
        date = datetime.datetime.strptime(r.date, '%d.%m.%Y').date()
        edge_type = r.type  # добавляем тип разгрузки на ребро
        edge_attrs = {'weight': weight, 'edge_type': edge_type}
        G.add_weighted_edges_from([(city1, city2, edge_attrs)])  # добавляем тип разгрузки на ребро

    # Ищем циклы, учитывая тип разгрузки на каждой точке маршрута
    target_edge_type = "любой"
    if target_edge_type == 'любой':
        valid_edge_types = ['любой', 'боковой', 'задний']
    elif target_edge_type == 'боковой':
        valid_edge_types = ['любой', 'боковой']
    elif target_edge_type == 'задний':
        valid_edge_types = ['любой', 'задний']

    # Ищем циклы, учитывая тип разгрузки на каждой точке маршрута
    cycles = []
    for node in NodeDBModel.select():
        for cycle in nx.simple_cycles(G, len(G.nodes)):
            valid_cycle = True
            for i in range(len(cycle) - 1):
                edge_data = G.get_edge_data(cycle[i], cycle[i + 1])
                edge_type = edge_data[0]['weight']['edge_type']  # получаем тип разгрузки на ребре
                if target_edge_type != edge_type not in target_edge_type:
                    valid_cycle = False
                    break

            if valid_cycle:
                cycles.append(cycle)

    answers = []
    for cycle in cycles:
        cycle_weight = 0
        for i in range(len(cycle) - 1):
            weight_dict = G.get_edge_data(cycle[i], cycle[i + 1])[0]['weight']
            weight = weight_dict['weight']
            edge_datetime = datetime.datetime.combine(date, weight)
            cycle_weight += edge_datetime.hour
        answers.append({'width': cycle_weight, 'len': len(cycle), 'cycle': cycle, 'edge_type': edge_type})
    answers = list(filter(lambda x: x['width'] > 0, answers))
    answers = sorted(answers, key=lambda x: (x['len'], -x['width']))
    pprint.pprint(answers[-1])
