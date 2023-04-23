from peewee import SqliteDatabase
from db.models import db_proxy, init_tables


database = SqliteDatabase('scal.db')


def init_db():
    db_proxy.initialize(database)
    init_tables(database)
