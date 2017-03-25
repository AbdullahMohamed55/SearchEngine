import timeit
from Model import *
from datetime import *
from time import sleep
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
            DB.create_tables([IndexerTable, UncrawledTable, CrawledTable, RobotTxts, WebPages, Seeds])
            Seeds(pageURL='https://www.reddit.com/', crawlFrequency=1, lastCrawl= datetime(1960, 1, 1, 1, 1, 1)).save()
            Seeds(pageURL='https://www.newsvine.com/', crawlFrequency=1, lastCrawl=datetime(1960, 1, 1, 1, 1, 1)).save()


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

        tryFor = 0 #times
        while(tryFor != 0):
            print("Indexer will try to index after 60 seconds.")
            sleep(60) #give time for crawling threads to add new urls
            self._indexCrawledPages()
            tryFor -= 1

        return

    '''Indexes newly crawled web pages'''
    def _indexCrawledPages(self):

        print("Indexing...")
        start = timeit.default_timer()
        count = 0
        try:
            print("WebPages table entries: ", WebPages.select().count())
            print("Crawled table entries: ", CrawledTable.select().count())
            print("Uncrawled table entries: ", UncrawledTable.select().count())

            for page in WebPages.select():

                count += 1
                self.indexer.update(page.pageURL, page.pageContent)
                # delete indexed page from WebPages table
                page.delete_instance()

        except OperationalError:
            print("Database got locked by a crawling thread!")
            print("This insertion will be skipped for now and resumed soon.")

        stop = timeit.default_timer()
        print("TOOK :: %.2f mins for indexing %d newly crawled web pages." % ((stop - start) / 60., count))


    def end(self):

        for i in range(len(self.crawlerObjs)):
            self.crawlerObjs[i].join()
        CrawledTable.delete().execute()
        UncrawledTable.delete().execute()
        RobotTxts.delete().execute()
        #index for the last time
        print("All crawling threads are done...")
        print("Indexing for the last time and terminating the Engine...")
        self._indexCrawledPages()
        #close db
        DB.close()

        return
