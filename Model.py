from peewee import *

db = SqliteDatabase('engine.db')

class BaseModel(Model):
    class Meta:
        database = db


class CrawledTable(BaseModel):

    craweledURLs = CharField(unique =True)

class UnCrawledTable(BaseModel):

    uncrawledURLs = CharField(unique = True)



class IndexerTable(BaseModel):

    name = CharField()
    birthday = DateField()



db.connect()

#in init onllyyy
#db.create_tables([CrawledTable, UnCrawledTable,IndexerTable])

#ahmed = CrawledTable.create(craweledURLs = "xxx.com")
#ahmed.save()
ahmed = CrawledTable.select().where(CrawledTable.craweledURLs == 'xxx.com').get()
print(ahmed)
ahmed.delete_instance()



