from sqlite_orm.database import Database
from sqlite_orm.field import IntegerField, BooleanField, TextField
from sqlite_orm.table import BaseTable


class User(BaseTable):
    __table_name__ = 'users'

    id = IntegerField(primary_key=True, auto_increment=True)  # Р°РІС‚РѕРёРЅРєСЂРµРјРµРЅС‚ РЅР° int РїРѕР»Рµ
    name = TextField(not_null=True)
    active = BooleanField(not_null=True, default_value=1)


with Database("test.db") as db:
    # create table
    db.query(User).drop().execute()
    db.query(User).create().execute()

    user1 = User(id=1, name='User1')
    user2 = User(id=2, name='User2')
    user3 = User(id=3, name='User3')
    db.query().insert(user1, user2, user3).execute()