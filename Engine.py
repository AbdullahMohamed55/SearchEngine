import timeit
import sqlite3
from time import sleep
from Model import *
from datetime import *
from Crawler import Crawler
from Indexer import Indexer


class Engine:

    def __init__(self):

        DB.connect()
        self._getDBTables()
        self.indexer = Indexer()
        self.numberOfThreads = 1
        self._setNumOfThreads()
        self.crawlerObjs = []
        self._createCrawlerObjects()


    def _getDBTables(self):

        if not DB.get_tables():
            print("Creating Database...")
            DB.create_tables([PageRank, IndexerTable, UncrawledTable, CrawledTable, RobotTxts, WebPages, Seeds])
            #Seeds(pageURL='https://www.reddit.com/', crawlFrequency=1, lastCrawl=datetime(1960, 1, 1, 1, 1, 1)).save()
            Seeds(pageURL='https://twitter.com/', crawlFrequency=1, lastCrawl= datetime(1960, 1, 1, 1, 1, 1)).save()
            #Seeds(pageURL='https://www.newsvine.com/', crawlFrequency=1, lastCrawl=datetime(1960, 1, 1, 1, 1, 1)).save()


    def _setNumOfThreads(self):

        self.numberOfThreads = input('Enter number of threads: ')
        while not self.numberOfThreads.isnumeric():
            self.numberOfThreads = input('Invalid input, please enter a valid number: ')


    def _createCrawlerObjects(self):
        Crawler.numberOfThreads = int(self.numberOfThreads)
        print('Creating ', self.numberOfThreads , ' crawler objects.')
        for i in range(int(self.numberOfThreads)):
            self.crawlerObjs.append(Crawler(i))


    '''create crawling threads and start indexing'''
    def start(self):

        for i in range(len(self.crawlerObjs)):
            self.crawlerObjs[i].start()

        tryFor = 1000000 #trials for indexer if WebPages table is found empty
        sleepFor = 60 #secs

        while(tryFor != 0):
            print("INDEXER: Indexer will try to index after %d seconds." % sleepFor)
            sleep(sleepFor)  # give time for crawling threads to add new urls
            self._indexCrawledPages()
            tryFor -= 1
            print("INDEXER: %d Trials left for indexer." % tryFor)
        return

    '''Indexes newly crawled web pages'''
    def _indexCrawledPages(self):

        print("INDEXER: Indexing started...")
        start = timeit.default_timer()
        count = 0
        while True:
            try:
                print("INDEXER: %d found web pages for indexing..." % WebPages.select().count())
                #print("Crawled table entries: ", CrawledTable.select().count())
                #print("Uncrawled table entries: ", UncrawledTable.select().count())

                for page in WebPages.select():

                    self.indexer.update(str(page.pageURL), str(page.pageContent))
                    # delete indexed page from WebPages table
                    page.delete_instance()
                    count += 1
                #WebPages is empty
                break

            except (OperationalError, sqlite3.OperationalError) as e:
                if 'binding' in str(e):
                    break
                print("INDEXER: DB Busy: Indexer is Retrying...'")
            except:
                break

        stop = timeit.default_timer()
        print("INDEXER: TOOK :: %.2f mins for indexing %d newly crawled web pages." % ((stop - start) / 60., count))


    def end(self):

        for i in range(len(self.crawlerObjs)):
            self.crawlerObjs[i].join()
        print("All crawling threads are done...")

        print("Indexing for the last time")
        self._indexCrawledPages()
        print("Emptying all tables and Terminating Engine...")
        try:
            CrawledTable.delete().execute()
            UncrawledTable.delete().execute()
            RobotTxts.delete().execute()
        except:
            print("DB Error: Couldn't delete all tables!")

        #close db
        DB.close()

        return
