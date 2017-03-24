from peewee import *

DB = SqliteDatabase("SearchEngine.db", threadlocals=True)

''''---------------------------------------------CRAWLER Stuff-------------------------------------------------------'''

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


''''---------------------------------------------INDEXER Stuff-------------------------------------------------------'''

class PositionsField(CharField):

    '''convert python data type for storage in the database'''
    def db_value(self, value):

        dbValue = ''
        for x in range(0,len(value)-1):
            dbValue += str(value[x])
            dbValue += ","

        if value:
            dbValue += str(value[len(value)-1])

        return dbValue

    '''convert data type from database to python '''
    def python_value(self, value):

        result = []
        for i in range(0,len(value),2):
            result.append(int(value[i]))

        return result


class IndexerTable(Model):

    keyword = CharField()
    url = CharField()
    positions = PositionsField(default = [])
    importance = IntegerField() # 0-> title , 1-> header, 2->plain text

    class Meta:
        database = DB
        primary_key = CompositeKey('keyword', 'url')
