import datetime
import json
import pprint
from itertools import count

import funcs
from db.models import RibDBModel
from settings import init_db
import networkx as nx
from db.models import NodeDBModel
import uvicorn
if __name__ == '__main__':
    init_db()

    node = NodeDBModel.select()[0]
    rib = RibDBModel.select().where(RibDBModel.from_node==node)

    answers = funcs.getRoutes()
    answers = funcs.remove_duplicates_from_json("answers.json")
    pprint.pprint(answers)


