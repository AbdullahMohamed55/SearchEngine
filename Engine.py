import timeit
import sqlite3
from time import sleep
from random import randint
from Model import *
from datetime import *
from Crawler import Crawler, NUMOFPAGES
from Indexer import Indexer


class Engine:

    def __init__(self):

        DBCrawl.connect()
        DBUnCrawl.connect()
        DBRobot.connect()
        DBWebPage.connect()
        DBPageRank.connect()
        DBIndexer.connect()
        indexedCount.connect()
        #DBQuery.connect()

        self._getDBTables()
        self.indexer = Indexer()
        self.numberOfThreads = 1
        self._setNumOfThreads()
        self.crawlerObjs = []
        self._createCrawlerObjects()


    def _getDBTables(self):

        if not DBCrawl.get_tables():
            print("Creating Crawl Database...")
            DBCrawl.create_tables([CrawledTable, Seeds])
            #Seeds(pageURL='https://www.reddit.com/', crawlFrequency=1, lastCrawl=datetime(1960, 1, 1, 1, 1, 1)).save()
            Seeds(pageURL='https://twitter.com/', crawlFrequency=1, lastCrawl= datetime(1960, 1, 1, 1, 1, 1)).save()
            #Seeds(pageURL='https://www.newsvine.com/', crawlFrequency=1, lastCrawl=datetime(1960, 1, 1, 1, 1, 1)).save()
        if not DBUnCrawl.get_tables():
            print("Creating UnCrawl Database...")
            DBUnCrawl.create_tables([UncrawledTable])
        if not DBRobot.get_tables():
            print("Creating Robot Database...")
            DBRobot.create_tables([RobotTxts])
        if not DBWebPage.get_tables():
            print("Creating WebPage Database...")
            DBWebPage.create_tables([WebPages])
        if not DBPageRank.get_tables():
            print("Creating PageRank Database...")
            DBPageRank.create_tables([PageRank])
        if not DBIndexer.get_tables():
            print("Creating Indexer Database...")
            DBIndexer.create_tables([IndexerTable])
        if not indexedCount.get_tables():
            print("Creating indexedCount var...")
            indexedCount.create_tables([IndexedCount])
            IndexedCount.insert().execute()
        if not DBPhrase.get_tables():
            print("Creating PhraseSearch Database...")
            DBPhrase.create_tables([FullPages])
        #if not DBQuery.get_tables():
        #    print("Creating Query Database...")
        #    DBQuery.create_tables([QuerySuggestion])



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

        tryFor = NUMOFPAGES #trials for indexer if WebPages table is found empty
        sleepFor =10 #secs
        self.indexed = IndexedCount.get(IndexedCount.id == 1).indexedURLs
        '''temp = IndexedCount.select().where(IndexedCount.id == 1)
        for x in temp:
            self.indexed = x.indexedURLs'''

        print(self.indexed)
        while(tryFor != 0):
            print("INDEXER: Indexer will try to index after %d seconds." % sleepFor)
            sleep(randint(1,sleepFor))  # give time for crawling threads to add new urls
            self._indexCrawledPages()
            tryFor -= 1
            print("INDEXER: %d Trials left for indexer." % tryFor)
        return

    '''Indexes newly crawled web pages'''
    def _indexCrawledPages(self):

        print("INDEXER: Indexing started...")
        start = timeit.default_timer()
        #count = 0
        #while True:
            #try:
        print("INDEXER: %d found web pages for indexing..." % (WebPages.select().count()))
        #print("Crawled table entries: ", CrawledTable.select().count())
        #print("Uncrawled table entries: ", UncrawledTable.select().count())
        selector =  WebPages.select().where(WebPages.id == self.indexed+1)
        for page in selector:

            self.indexer.update(str(page.pageURL), str(page.pageContent))
            self.indexed += 1
            #sleep(randint(1,5))
            '''if(self.indexed % 100 == 1):
                while True:
                    try:
                        # delete indexed page from WebPages table
                        dell =WebPages.delete().where(WebPages.id <= self.indexed)
                        dell.execute()
                        print("INDEXER: Deleted old entries from WebPages table")
                        break
                    except (OperationalError, sqlite3.OperationalError) as e:
                        if 'binding' in str(e):
                            break
                        print('INDEXER: Database busy, retrying. WebPage delete')
                        sleep(randint(1,10))
                    except:
                        break'''
        #WebPages is empty
        IndexedCount.update(indexedURLs=self.indexed).where(IndexedCount.id == 1).execute()
        '''break
    except (OperationalError, sqlite3.OperationalError) as e:
        if 'binding' in str(e):
            break
        print("INDEXER: DB Busy: Indexer is Retrying...'")
        sleep(randint(1, 10))
    except:
        break'''

        stop = timeit.default_timer()
        print("INDEXER: TOOK :: %.2f mins, %d indexed web pages." % ((stop - start) / 60., self.indexed))


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
        DBCrawl.close()
        DBUnCrawl.close()
        DBWebPage.close()
        DBRobot.close()
        DBIndexer.close()
        DBPageRank.close()
        indexedCount.close()

        return
