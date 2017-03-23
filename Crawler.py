import urllib.request
import urllib.response
import urllib.parse
import urllib.robotparser
import threading
import os
from datetime import *
import time
from Model import *

import bs4

from html.parser import HTMLParser
#

NUMOFPAGES = 10000
class MyHTMLParser(HTMLParser):
    def __init__(self, currentLink):
        HTMLParser.__init__(self)
        self.links = []
        self.parsingLink = currentLink
    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    link = value
                    if link.startswith('//'):
                        link = 'http:' + link
                    elif link.startswith('/'):
                        link = urllib.parse.urljoin(self.parsingLink, link)
                    if '#' in link:
                        continue
                    elif link.startswith('ftp'):
                        continue
                    elif link.startswith('javascript'):
                        continue
                    parsedLink = urllib.parse.urlparse(link)
                    link = parsedLink.scheme + '://' + parsedLink.netloc
                    if link[-1] != '/':
                        link = link + '/'
                    self.links.append({'uncrawledURL': link})
#
class Crawler(threading.Thread):

    dbLock = threading.Lock()
    def __init__(self, cID):
        threading.Thread.__init__(self)
        self.crawlerID = cID
        for seed in Seeds.select():
            if UncrawledTable.select().where(UncrawledTable.uncrawledURL == seed.pageURL).exists():
                continue
            timeDifference = datetime.now() - seed.lastCrawl
            timeDifferenceInHours = timeDifference.days * 24 + timeDifference.seconds // 3600
            if timeDifferenceInHours >= seed.crawlFrequency:
                UncrawledTable.get_or_create(uncrawledURL = seed.pageURL)
                seed.lastCrawl = datetime.now()
                seed.save()

    def run(self):
        tryTwice = 0
        while True:

            ##
            Crawler.dbLock.acquire()
            ###############################
            print('Thread ' + str(self.crawlerID) + ': Lock acquired, Getting link.')
            if WebPages.select().count() == NUMOFPAGES:
                print('Thread ' + str(self.crawlerID) + ': Target reached, ending crawl')
                break
            linkQuery = UncrawledTable.select().limit(1)
            if not linkQuery.exists():
                Crawler.dbLock.release()
                if tryTwice == 2:
                    print('Thread ' + str(self.crawlerID) + ': No links available. Ending crawl.')
                    break
                print('Thread ' + str(self.crawlerID) + ': No links available. Sleeping for 60 seconds. Attempt: ' + str(tryTwice + 1))
                time.sleep(60)
                tryTwice = tryTwice + 1
                continue
            tryTwice = 0
            linkQuery = linkQuery.get()
            link = linkQuery.uncrawledURL
            linkQuery.delete_instance()
            CrawledTable(crawledURL=link).insert().upsert()
            print('Thread ' + str(self.crawlerID) + ': Done getting link, releasing lock.')
            ################################
            Crawler.dbLock.release()
            ##
            print('Thread ' + str(self.crawlerID) + ': Crawling link: ' + link)
            self.crawl(link)
            print('Thread ' + str(self.crawlerID) + ': Done crawling link: ' + link)
        CrawledTable.delete().execute()
        UncrawledTable.delete().execute()
        RobotTxts.delete().execute()



    def crawl(self, link):
        if CrawledTable.select().where(CrawledTable.crawledURL == link).exists():
            print('Thread ' + str(self.crawlerID) + ': Link already visited.')
            return
        tryOnce = 0
        robotParser = self.setupRobotParser(link)
        if robotParser.can_fetch("*", link):
            while True:
                try:
                    response = urllib.request.urlopen(link)
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        if tryOnce == 1:
                            print(
                                'Thread ' + str(self.crawlerID) + ': Too many requests: ' + link + ' returning.')
                            return
                        print('Thread ' + str(self.crawlerID) + ': Too many requests: ' + link + ' trying again in 120 seconds.')
                        time.sleep(120)
                        tryOnce = 1
                    else:
                        return

            returnedLink = response.geturl()
            if returnedLink != link:
                print('Thread ' + str(self.crawlerID) + ': Redirection:' + link + ' returning.')
                return

            urlInfo = response.info()
            dataType = urlInfo.get_content_type()
            if 'html' not in dataType:
                print('Thread ' + str(self.crawlerID) + ': Not HTML ' + link + ' returning.')
                return

            webContent = str(response.read())

            if WebPages.select().where(WebPages.pageURL == returnedLink).exists():
                WebPages.update(pageContent = webContent).where(WebPages.pageURL == returnedLink).execute()
            else:
                print('Thread ' + str(self.crawlerID) + ': Saving webpage ' + link )
                WebPages(pageURL = returnedLink, pageContent = webContent).save()
            print('Thread ' + str(self.crawlerID) + ': Done saving webpage and starting link extraction ' + link)
            parser = MyHTMLParser(link)
            parser.feed(str(webContent))
            with DB.atomic():
                UncrawledTable.insert_many(parser.links).upsert().execute()
            print('Thread ' + str(self.crawlerID) + ': Done inserting links ' + link)
    def setupRobotParser(self, url):
        rp = urllib.robotparser.RobotFileParser()

        currentUrlComponents = urllib.parse.urlparse(url)
        robotLocation = urllib.parse.urljoin(currentUrlComponents.scheme + '://' + currentUrlComponents.netloc, 'robots.txt')
        robotQuery = RobotTxts.select().where(RobotTxts.netLoc == robotLocation)
        if robotQuery.exists():
            robotData = robotQuery.get()
            rp.parse(str(robotQuery.get().robotContent))
        else:
            try:
                robotContentFromInternet = str(urllib.request.urlopen(robotLocation).read())
            except:
                robotContentFromInternet = ''

            rp.parse(robotContentFromInternet)
            RobotTxts(netLoc = robotLocation, robotContent = robotContentFromInternet).save()



        return rp