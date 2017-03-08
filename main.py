from Model import *
from Crawler import Crawler
from Indexer import Indexer


SEED_PATH = 'seeds.txt'
DOWNLOAD_PATH = './pages/'

#crawlerObj = Crawler(SEED_PATH, DOWNLOAD_PATH)
#crawlerObj.start()

DB.connect()

"""RUN this only once when creating tables!"""
#sDB.create_tables([IndexerTable,UnCrawledTable,CrawledTable])

"""our engine starts here"""

DB.close()