import datetime
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import networkx as nx
from db.models import NodeDBModel, RibDBModel

app = FastAPI()


class CycleResponse(BaseModel):
    start: str
    end: str
    date: str
    times: List[float]
    travel_times: List[float]


def build_cycle_response(cycle, travel_times):
    response = CycleResponse(
        start=cycle[0],
        end=cycle[-1],
        date=datetime.datetime.strptime(travel_times[0]['date'], '%d.%m.%Y').strftime('%Y-%m-%d'),
        times=[float(datetime.datetime.strptime(t['time'], '%H:%M').strftime('%H.%M')) for t in travel_times],
        travel_times=travel_times,
    )
    return response


def get_cycles(target_edge_type):
    cycles = []
    G = nx.MultiDiGraph()

    for r in RibDBModel.select():
        city1 = r.from_node.title
        city2 = r.to_node.title
        weight = r.time
        date = datetime.datetime.strptime(r.date, '%d.%m.%Y').date()
        edge_type = r.type
        edge_attrs = {'weight': weight, 'edge_type': edge_type}
        G.add_weighted_edges_from([(city1, city2, edge_attrs)])

    for node in NodeDBModel.select():
        for cycle in nx.simple_cycles(G, len(G.nodes)):
            valid_cycle = True
            travel_times = []
            for i in range(len(cycle) - 1):
                edge_data = G.get_edge_data(cycle[i], cycle[i + 1])

                edge_type = edge_data[0]['weight']['edge_type']
                if target_edge_type != edge_type not in target_edge_type:
                    valid_cycle = False
                    break

                travel_times.append({
                    'from': cycle[i],
                    'to': cycle[i + 1],
                    'date': date.strftime('%d.%m.%Y'),
                    'time': edge_data[0]['weight']['weight'],
                })

            if valid_cycle:
                cycles.append((cycle, travel_times))

    return cycles