#author: Lixuan Yang, Chenfeng Fan, Ye Hong, Limian Guo
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase, JSONField
from playhouse.migrate import *
db = SqliteExtDatabase('user_statistic.db')


class Query(Model):
    id = IntegerField(primary_key=True)
    query = CharField()
    result = CharField()  # we store JSON here for the results

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
    field = CharField()

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
# perform migrate
# http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#migrate
# db.drop_tables([Query, Hover, Click, Drag, Stay])
db.create_tables([Query, Hover, Click, Drag, Stay])
