from datetime import datetime

from peewee import CharField, DateField, UUIDField, TimeField, IntegerField, DateTimeField
from peewee import Model, DatabaseProxy, ForeignKeyField
from peewee import SqliteDatabase
import bcrypt
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


class RouteDBModel(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    cycle = CharField()
    weight = IntegerField()
    length = IntegerField()
    edge_type = CharField()
    start_date = DateField()
    end_date = DateField()
    cityfrom = CharField()
    cityto = CharField()

    class Meta:
        db_table = 'routes'
        database = db_proxy


class UserDBModel(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    login = CharField(unique=True)
    password_hash = CharField()
    registration_date = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'users'
        database = db_proxy

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class ModeratorDBModel(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    login = CharField(unique=True)
    registration_date = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'moderators'
        database = db_proxy


class AdminDBModel(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    login = CharField(unique=True)
    registration_date = DateTimeField(default=datetime.now)

    # Relationships
    user = ForeignKeyField(UserDBModel, backref='admin', null=True)  # Admin is associated with a User
    moderator = ForeignKeyField(ModeratorDBModel, backref='admin', null=True)  # Admin is associated with a Moderator

    class Meta:
        db_table = 'admins'
        database = db_proxy


def init_tables(db: SqliteDatabase):
    with db:
        db.create_tables([
            NodeDBModel,
            RibDBModel,
            RouteDBModel,
            UserDBModel,
            AdminDBModel,
            ModeratorDBModel,
        ])
        db.commit()
