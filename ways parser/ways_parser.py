from db.models import NodeDBModel, RibDBModel

from typing import Union
import csv
import re

from pydantic import BaseModel, validator


class NodesModel(BaseModel):
    node1: Union[str]
    node2: Union[str]
    date: Union[str]
    time: Union[str]
    carg_type: Union[str]

    @validator('time')
    def _time_validator(cls, v):
        if not v:
            return '00:00:00'
        return v

    @validator('node1', 'node2')
    def _node_validator(cls, v):
        add_dots_list = ['г', 'п', 'обл', 'с', 'респ', 'р-н', 'мо']
        replace_values = {
            ' район ': ' р-н ',
            ' город ': ' г ',
            ' посёлок ': ' п ',
            ' область ': ' обл ',
            ' республика ': ' респ ',
            ' село ': ' с ',
        }
        sp_addr = v.lower().split(',')
        for _i in range(len(sp_addr)):
            t_sp_n = f' {sp_addr[_i]} '
            for _r in replace_values.keys():
                if _r in t_sp_n:
                    t_sp_n = t_sp_n.replace(_r, replace_values[_r])
            for _d in add_dots_list:
                _d_with_dot = f' {_d}. '
                points = [',', '']
                for _p in points:
                    if f' {_d}{_p} ' in t_sp_n:
                        t_sp_n = t_sp_n.replace(f' {_d}{_p} ', _d_with_dot)
                if t_sp_n.endswith(_d_with_dot):
                    t_sp_n = _d_with_dot + t_sp_n[:len(t_sp_n) - len(_d_with_dot)]
            sp_addr[_i] = ' '.join(t_sp_n.split())
        return ', '.join(sp_addr)


class WaysParser(object):
    @classmethod
    def load_data(cls, file_name: Union[str]) -> None:
        with open(file_name, 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            for row in csv_reader:
                nodes = NodesModel(node1=row[1], node2=row[2], date=row[3], time=row[4], carg_type=row[5])
                nodes_list = [nodes.node1, nodes.node2]
                for _n in range(len(nodes_list)):
                    # No Sqlite
                    # ribs = NodeDBModel.select().where(NodeDBModel.title.regexp(f'{nodes_list[_n]}[^А-Яа-яЁё]*$')).dicts()
                    # Sqlite
                    find = False
                    for _nr in NodeDBModel.select():
                        match = re.search(f'{nodes_list[_n]}[^А-Яа-яЁё]*$', _nr.title)
                        if match:
                            find = True
                            nodes_list[_n] = _nr
                            break
                    if not find:
                         nodes_list[_n] = NodeDBModel.get_or_create(title=nodes_list[_n])[0]
                RibDBModel.get_or_create(from_node=nodes_list[0], to_node=nodes_list[1],
                                         date=nodes.date, time=nodes.time, type=nodes.carg_type)

    # def remove_clones(self):
    #     for _n in NodeDBModel.select():
    #         count_rows = NodeDBModel.select().where(NodeDBModel.title.contains(' ' + _n.title + ' ')).count()
    #         if count_rows > 1:
    #             print(_n.title)
    #             NodeDBModel.delete().where(NodeDBModel.uuid == _n.uuid).execute()
