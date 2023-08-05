import datetime
from datetime import date
import json
import pprint
import uuid

import networkx as nx
import requests
import time

from db.models import NodeDBModel, RibDBModel, RouteDBModel
from settings import init_db


def get_coordinates(city_name):
    formatted_city = city_name
    url = f'https://api.openrouteservice.org/geocode/search?api_key=5b3ce3597851110001cf62482a313763d43c43699380e8b5dc181d5e&text={formatted_city}&boundary.country=RUS&sources=whosonfirst'
    response = requests.get(url)
    result = json.loads(response.content)
    if result and result.get('bbox'):
        lat, lon = result.get('bbox')[0], result.get('bbox')[1]
        print(lat, lon)
        return lat, lon
    else:
        print(f"No coordinates found for {formatted_city} Response{response.text}")
        return None, None


def get_route(from_city, to_city):
    from_coords = get_coordinates(from_city)
    print(from_city, from_coords)
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
    print(distance, "дистанция", duration, "время")
    return distance, duration, None


def remove_duplicates_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    unique_data = []
    for record in data:
        if 'city' in record:
            city = record['city']
            is_unique = True
            for unique_record in unique_data:
                if 'city' in unique_record:
                    if all(city.get(key) == unique_record['city'].get(key) for key in city.keys() if key != 'id'):
                        is_unique = False
                        break
            if is_unique:
                unique_data.append(record)

    with open(filename, 'w') as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)

    with open(filename, 'r') as f:
        return json.load(f)


def remove_duplicates_from_json_test(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    unique_data = []
    for record in data:
        if 'city' in record:
            city = record['city']
            is_unique = True
            for unique_record in unique_data:
                if city in tuple(unique_record):
                    if all(city.get(key == unique_record['city'].get(key) for key in city.keys() if key != 'id')):
                        is_unique = False
                        break
            if is_unique:
                unique_data.append(record)

    with open(filename, 'w') as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)

    with open(filename, 'r') as f:
        return json.load(f)


def getRoutes():
    G = nx.MultiDiGraph()
    for r in RibDBModel.select():
        city1 = r.from_node.title
        city2 = r.to_node.title

        weight = r.time
        date = datetime.datetime.strptime(r.date, '%d.%m.%Y').date()
        edge_attrs = {'weight': weight, 'edge_type': r.type, 'date': date}
        G.add_weighted_edges_from([(city1, city2, edge_attrs)])

    target_edge_type = "любой"
    if target_edge_type == 'любой':
        valid_edge_types = ['любой', 'боковой', 'задний']
    elif target_edge_type == 'боковой':
        valid_edge_types = ['любой', 'боковой']
    elif target_edge_type == 'задний':
        valid_edge_types = ['любой', 'задний']

    cycles = []
    id = 0
    for node in NodeDBModel.select():
        for cycle in nx.simple_cycles(G, len(G.nodes)):
            valid_cycle = True
            for i in range(len(cycle) - 1):
                edge_data = G.get_edge_data(cycle[i], cycle[i + 1])
                edge_type = edge_data[0]['weight']['edge_type']
                if target_edge_type != 'любой' and edge_type not in valid_edge_types:
                    valid_cycle = False
                    break
                if i == 0:
                    start_time = edge_data[0]['weight']['date']
                elif i == len(cycle) - 2:
                    end_time = edge_data[0]['weight']['date']
                    if start_time == end_time and end_time < start_time:
                        valid_cycle = False
                        break

            if valid_cycle:
                cycles.append(cycle)

    answers = []
    for cycle in cycles:
        ...
        cycle_dates = []
        cycle_weight = 0
        cycle_dates = []
        from_city = cycle[0]
        to_city = cycle[-1]

        first_edge = None
        for i in range(len(cycle) - 1):
            edge = G.get_edge_data(cycle[i], cycle[i + 1])
            if edge:
                first_edge = edge[0]
                break

        if first_edge is not None:
            start_date = first_edge['weight']['date']
            formatted_start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()

            last_edge = None
            for i in range(len(cycle) - 1):
                edge = G.get_edge_data(cycle[i], cycle[i + 1])
                if edge:
                    last_edge = edge[0]

            if last_edge is not None:
                end_date = last_edge['weight']['date']
                formatted_end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
                if (formatted_start_date < formatted_end_date):
                    interval = formatted_end_date - formatted_start_date
                    if interval <= datetime.timedelta(days=2):

                        for i in range(len(cycle) - 1):
                            edge_data = G.get_edge_data(cycle[i], cycle[i + 1])
                            weight_dict = edge_data[0]['weight']
                            weight = weight_dict['weight']
                            edge_datetime = datetime.datetime.combine(weight_dict['date'], weight)
                            cycle_dates.append(edge_datetime.date())
                            cycle_weight += edge_datetime.hour

                            if i == 0:
                                from_city_type = edge_data[0]['weight'].get('edge_type')

        id += 1
        answers.append({
            'city': {
                'weight': cycle_weight,
                'len': len(cycle),
                'cycle': cycle,
                'edge_type': edge_type,
                'start_date': datetime.datetime.strptime(str(formatted_start_date), '%Y-%m-%d').strftime('%d.%m.%Y'),
                'end_date': datetime.datetime.strptime(str(formatted_end_date), '%Y-%m-%d').strftime('%d.%m.%Y'),

                'from': from_city,
                'to': to_city,
            }})

    answers = list(filter(lambda x: x['city']['weight'] > 0, answers))
    answers = sorted(answers, key=lambda x: (x['city']['len'], -x['city']['weight']))
    for answer in answers:

        city_data = answer['city']
        cycle_str = ', '.join(city_data['cycle'])
        try:
            RouteDBModel.get_or_create(
                cycle=cycle_str,
                weight=city_data['weight'],
                length=city_data['len'],
                edge_type=city_data['edge_type'],
                start_date=datetime.datetime.strptime(city_data['start_date'], '%d.%m.%Y'),
                end_date=datetime.datetime.strptime(city_data['end_date'], '%d.%m.%Y'),
                cityfrom=city_data['from'],
                cityto=city_data['to']
            )
        except Exception as e:
            print(f"Error occurred while inserting data: {e}")

    with open('answers.json', 'w') as f:
        json.dump(answers, f, ensure_ascii=False, indent=4)
    return answers
