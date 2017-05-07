from peewee import *

DBCrawl = SqliteDatabase("CrawlTable.db", threadlocals=True)
DBUnCrawl = SqliteDatabase("UnCrawlTable.db", threadlocals=True)
DBRobot = SqliteDatabase("RobotTable.db", threadlocals=True)
DBWebPage = SqliteDatabase("WebPageTable.db", threadlocals=True)
DBPageRank = SqliteDatabase("PageRankTable.db", threadlocals=True)
DBIndexer = SqliteDatabase("IndexerTable.db", threadlocals=True)
DBQuery = SqliteDatabase("QueryTable.db", threadlocals=True)
indexedCount = SqliteDatabase("indexedCount.db", threadlocals=True)

''''---------------------------------------------CRAWLER Stuff-------------------------------------------------------'''

class CrawledTable(Model):

    crawledURL = CharField(unique =True)

    class Meta:
        database = DBCrawl

class UncrawledTable(Model):

    uncrawledURL = CharField(unique = True)

    class Meta:
        database = DBUnCrawl

class RobotTxts(Model):

    netLoc = CharField(unique=True)
    robotContent = TextField()

    class Meta:
        database = DBRobot

class WebPages(Model):

    pageURL = CharField(unique=True)
    pageContent = TextField()

    class Meta:
        database = DBWebPage

class Seeds(Model):

    pageURL = CharField(unique=True)
    crawlFrequency = IntegerField()
    lastCrawl = DateTimeField()

    class Meta:
        database = DBCrawl

''''---------------------------------------------Page InLinks Stuff-------------------------------------------------------'''
class PageRank(Model):
    pageURL = CharField(unique=True)
    pageInLinks = IntegerField(default = 1)

    class Meta:
        database = DBPageRank

''''---------------------------------------------Search Suggestions Stuff-------------------------------------------------------'''
class QuerySuggestion(Model):
    keyword = CharField(unique=True)
    stem = CharField()
    count = IntegerField(default = 1)

    class Meta:
        database = DBQuery

''''---------------------------------------------INDEXER Stuff-------------------------------------------------------'''
class IndexedCount(Model):
    indexedURLs= IntegerField(default=0)

    class Meta:
        database = indexedCount

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
        database = DBIndexer
        primary_key = CompositeKey('keyword', 'url')
