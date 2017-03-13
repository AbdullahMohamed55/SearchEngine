from Model import *
from Crawler import Crawler
from Indexer import Indexer
from datetime import *
import os

DB.connect()

"""RUN this only once when creating tables!"""
if not DB.get_tables():
    DB.create_tables([IndexerTable, UncrawledTable, CrawledTable, RobotTxts, WebPages, Seeds])
    Seeds(pageURL = 'https://www.reddit.com', crawlFrequency = 0, lastCrawl = datetime(1960, 1, 1, 1, 1, 1)).save()

"""our engine starts here"""
crawlerObj = Crawler()
crawlerObj.start()

DB.close()