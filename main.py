from Model import *
from Crawler import Crawler
from Indexer import Indexer
from datetime import *
import threading

import os

DB.connect()

"""RUN this only once when creating tables!"""
if not DB.get_tables():
    DB.create_tables([IndexerTable, UncrawledTable, CrawledTable, RobotTxts, WebPages, Seeds])
    Seeds(pageURL = 'https://www.reddit.com', crawlFrequency = 0, lastCrawl = datetime(1960, 1, 1, 1, 1, 1)).save()

"""our engine starts here"""


numberOfThreads = input('Enter number of threads: ')
while not numberOfThreads.isnumeric():
    numberOfThreads = input('Invalid input, please enter a valid number: ')

crawlerObjs = []

print('Creating ' + numberOfThreads + ' crawler objects.')
for i in range (int(numberOfThreads)):
    crawlerObjs.append(Crawler(i))

for i in range (len(crawlerObjs)):
    crawlerObjs[i].start()

for i in range (len(crawlerObjs)):
    crawlerObjs[i].join()


DB.close()