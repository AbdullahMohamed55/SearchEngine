from Indexer import *
from Crawler import *
import timeit

'''whenever we crawl and webpages table gets updated, we then index the newly crawled pages'''

class Controller:

    def __init__(self):

        self.pageUrl = []
        self.pageContent = []
        self.indexer = Indexer()

    def checkIfCrawled(self, url):
        pass

    '''
    # loop on new urls in database and parse their documents
    def _getCrawledPages(self):

        pass #just for newly crawled!
        for page in  WebPages.select():
            self.pageUrl.append(page.pageURL)
            self.pageContent.append(page.pageContent)
    '''

    def indexCrawledPages(self):
        start = timeit.default_timer()
        #self._getCrawledPages()

        #for url, content in self.pageUrl,self.pageContent:
        for page in WebPages.select(): #TODO .where(newly cralwed)!
            self.indexer.update(page.pageURL,page.pageContent)

        stop = timeit.default_timer()
        print("TOOK ME ::" , stop-start, "secs")


'''
xx = Controller()
xx.indexCrawledPages()
'''