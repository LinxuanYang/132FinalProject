from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase,JSONField


db = SqliteExtDatabase('user_statistic.db')


class Query(Model):
    id = IntegerField(primary_key=True)
    query = CharField()
    result = JSONField()  # we store JSON here for the results

    class Meta:
        database = db  # This model uses the "people.db" database.

class Hover(Model):
    duration = BigIntegerField()
    query_id = ForeignKeyField(Query, backref='hovers')
    document_id = CharField()

    class Meta:
        database = db


class Click(Model):
    query_id = ForeignKeyField(Query, backref='clicks')
    document_id = CharField()

    class Meta:
        database = db


class Stay(Model):
    duration = BigIntegerField()
    query_id = ForeignKeyField(Query, backref='stays')
    document_id = CharField()

    class Meta:
        database = db


class Drag(Model):
    query_id = ForeignKeyField(Query, backref='drags')
    document_id = CharField()

    class Meta:
        database = db


db.connect()

db.create_tables([Query, Hover, Click, Drag, Stay])
