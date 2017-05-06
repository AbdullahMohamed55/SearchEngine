from peewee import *

DBCrawl = SqliteDatabase("EngineCrawl.db", threadlocals=True)
DBSearch = SqliteDatabase("EngineSearch.db", threadlocals=True)

''''---------------------------------------------CRAWLER Stuff-------------------------------------------------------'''

class BaseModel(Model):
    class Meta:
        database = DBCrawl


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

''''---------------------------------------------Page InLinks Stuff-------------------------------------------------------'''
class PageRank(Model):
    pageURL = CharField(unique=True)
    pageInLinks = IntegerField(default = 1)

    class Meta:
        database = DBSearch

''''---------------------------------------------Search Suggestions Stuff-------------------------------------------------------'''
class QuerySuggestion(Model):
    keyword = CharField(unique=True)
    stem = CharField()
    count = IntegerField(default = 1)

    class Meta:
        database = DBSearch

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
    stem = CharField()
    url = CharField()
    positions = PositionsField(default = [])
    importance = IntegerField() # 0-> title , 1-> header, 2->plain text

    class Meta:
        database = DBSearch
        primary_key = CompositeKey('keyword', 'url')
