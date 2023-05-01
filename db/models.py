from peewee import CharField, DateField, UUIDField, TimeField, IntegerField
from peewee import Model, DatabaseProxy, ForeignKeyField
from peewee import SqliteDatabase

import uuid

db_proxy = DatabaseProxy()


class NodeDBModel(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    title = CharField(max_length=120, unique=True)

    class Meta:
        db_table = 'nodes'
        database = db_proxy


class RibDBModel(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    from_node = ForeignKeyField(NodeDBModel, backref='ribs', on_delete='CASCADE')
    to_node = ForeignKeyField(NodeDBModel, backref='ribs', on_delete='CASCADE')
    date = DateField()
    time = TimeField(default=0)
    type = CharField(max_length=10)

    class Meta:
        db_table = 'ribs'
        database = db_proxy


def init_tables(db: SqliteDatabase):
    with db:
        db.create_tables([
            NodeDBModel,
            RibDBModel
        ])
        db.commit()

