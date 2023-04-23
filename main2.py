import datetime
import json
import pprint
from itertools import count

from db.models import RibDBModel
from settings import init_db
import networkx as nx
from db.models import NodeDBModel
import uvicorn
if __name__ == '__main__':
    init_db()

    node = NodeDBModel.select()[0]
    rib = RibDBModel.select().where(RibDBModel.from_node==node)

    # node.create(title='Город тест')
    # node.create(title='город тест2')
    # node.create(title='город тест3')
    # node.create(title='город тест4')
    node_test = NodeDBModel.select().where(NodeDBModel.title == "Город тест").first()
    node_test2 = NodeDBModel.select().where(NodeDBModel.title == "город тест2").first()
    node_test3 = NodeDBModel.select().where(NodeDBModel.title == "город тест3").first()
    node_test4 = NodeDBModel.select().where(NodeDBModel.title == "город тест4").first()
    # RibDBModel.create(from_node_id=f'{node_test.uuid}',to_node_id=f'{node_test2.uuid}',date='26.04.2023',time='02:00:00',type='любой')
    # RibDBModel.create(from_node_id=f'{node_test2.uuid}', to_node_id=f'{node_test3.uuid}', date='27.04.2023', time='02:00:00',type='любой')
    # RibDBModel.create(from_node_id=f'{node_test3.uuid}', to_node_id=f'{node_test4.uuid}', date='28.04.2023', time='02:00:00',
    #                   type='любой')
    # RibDBModel.create(from_node_id=f'{node_test2.uuid}', to_node_id=f'{node_test3.uuid}', date='29.04.2023', time='02:00:00',
    #                   type='любой')
    # RibDBModel.create(from_node_id=f'{node_test4.uuid}', to_node_id=f'{node_test.uuid}', date='30.04.2023', time='02:00:00',
    #                   type='любой')
    # RibDBModel.create(from_node_id=f'{node_test4.uuid}', to_node_id=f'115100a9dcfc40a699dbc4dce2be75db',
    #                   date='20.04.2023', time='02:00:00',
    #                   type='любой')
    # RibDBModel.create(from_node_id=f'872f91c8b2794bd8a8f589728af92767', to_node_id=f'{node_test4.uuid}', date='20.04.2023', time='02:00:00',
    #                   type='любой')
    # print(node_test.uuid,node_test2.uuid)








    G = nx.MultiDiGraph()
    for r in RibDBModel.select():
        city1 = r.from_node.title
        city2 = r.to_node.title
        # duration, distance = funcs.get_route(city1, city2)[:2]
        # time = duration
        weight = r.time
        date = datetime.datetime.strptime(r.date, '%d.%m.%Y').date()
        edge_type = r.type  # добавляем тип разгрузки на ребро
        edge_attrs = {'weight': weight, 'edge_type': edge_type, 'date': date}
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
    id=0
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
        for i, city in enumerate(cycle):
            if i < len(cycle) - 1:
                edge = G.get_edge_data(city, cycle[i + 1])
                if edge:
                    first_edge = edge[0]
                    break
        start_date = str(first_edge['weight']['date'])
        formatted_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d.%m.%Y')

        cycle_weight = 0
        cycle_dates = []
        for i in range(len(cycle) - 1):
            edge_data = G.get_edge_data(cycle[i], cycle[i + 1])
            weight_dict = edge_data[0]['weight']
            weight = weight_dict['weight']
            edge_datetime = datetime.datetime.combine(weight_dict['date'], weight)
            cycle_dates.append(edge_datetime.date())
            cycle_weight += edge_datetime.hour


        id += 1
        answers.append({'weight': cycle_weight, 'len': len(cycle), 'cycle': cycle, 'edge_type': edge_type,'start_date':formatted_date ,'end_date': r.date })


    answers = list(filter(lambda x: x['weight'] > 0, answers))
    answers = sorted(answers, key=lambda x: (x['len'], -x['weight']))
    pprint.pprint(answers)


    # uvicorn.run('FastApi:app', host='127.0.0.1', port=8000, reload=True)






    with open('answers.json', 'w') as f:
        json.dump(answers, f,ensure_ascii=False, indent=4)

    with open('answers.json', 'r')as f:
        data = json.load(f)

    # Удаление дубликатов из списка
    unique_data = list({json.dumps(item, sort_keys=True) for item in data})

    # Запись уникальных данных в файл
    with open('result.json', 'w',encoding='utf-8') as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)