from peewee import *

DB = SqliteDatabase("SearchEngine.db", threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = DB


class CrawledTable(BaseModel):

    crawledURL = CharField(unique =True)

class UncrawledTable(BaseModel):

    uncrawledURL = CharField(unique = True)

class RobotTxts(BaseModel):
    netLoc = CharField(unique=True)
    robotContent = TextField()

class WebPages(BaseModel):
    pageURL = CharField(unique=True)
    pageContent = TextField()

class Seeds(BaseModel):
    pageURL = CharField(unique=True)
    crawlFrequency = IntegerField()
    lastCrawl = DateTimeField()

"""INDEXER STUFF"""

class PositionsField(CharField):

    '''convert python datatype for storage in the database'''
    def db_value(self, value):

        dbValue = ''
        for x in range(0,len(value)-1):
            dbValue += str(value[x])
            dbValue += ","

        if value:
            dbValue += str(value[len(value)-1])
        #print(dbValue)
        return dbValue

    '''convert datatype from database to python '''
    def python_value(self, value):

        result = []
        for i in range(0,len(value),2):
            result.append(int(value[i]))

        #print (result)
        return result

class IndexerTable(Model):

    keyword = CharField()
    url = CharField()
    positions = PositionsField(default = [])
    importance = IntegerField() # 0-> title , 1-> header, 2->plain text

    class Meta:
        database = DB
        primary_key = CompositeKey('keyword', 'url')


'''

DB.connect()

#in init onllyyy
DB.create_tables([IndexerTable])

ahmed = IndexerTable.create(keyword = "bibo",urls ="www.vvv.com", positions = "123")
#ahmed.urls.append("www.vvv.com")
#ahmed.save()
#ahmed = IndexerTable.select().where(IndexerTable.urls == 'www.vvv.com').get()
##OR SIMPLY
#ahmed = IndexerTable.get(IndexerTable.keyword == 'bibo')
print(ahmed.urls , ahmed.positions)
#ahmed.delete_instance()
l = list(ahmed.positions)

print(int(l[0]))
#ahmed.positions = l
#ahmed.save()
print(ahmed.urls , ahmed.positions)
#print(IndexerTable.get(IndexerTable.keyword == 'bibo').positions)

DB.close()
'''