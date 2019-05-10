from peewee import *

db = SqliteDatabase('user_statistic.db')


class Query(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db  # This model uses the "people.db" database.


class Hover(Model):
    class Meta:
        database = db


class Click(Model):
    class Meta:
        database = db


class Stay(Model):
    class Meta:
        database = db


class Drag(Model):
    class Meta:
        database = db


db.connect()
db.create_tables([Query, Hover, Click, Drag, Stay])
