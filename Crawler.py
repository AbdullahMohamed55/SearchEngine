import urllib.request
import urllib.response
import urllib.parse
import urllib.robotparser
import os
from datetime import *
from Model import *

import bs4

from html.parser import HTMLParser
#
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
                    elif link.startswith('#'):
                        continue
                    elif link.startswith('ftp'):
                        continue
                    elif link.startswith('javascript'):
                        continue
                    self.links.append(link)
#
class Crawler:
    def __init__(self):
        for seed in Seeds.select():
            if UncrawledTable.select().where(UncrawledTable.uncrawledURL == seed.pageURL).exists():
                continue
            timeDifference = datetime.now() - seed.lastCrawl
            timeDifferenceInHours = timeDifference.days * 24 + timeDifference.seconds // 3600
            if timeDifferenceInHours >= seed.crawlFrequency:
                UncrawledTable(uncrawledURL = seed.pageURL).save()
                seed.lastCrawl = datetime.now()
                seed.save()

    def start(self):
        while True:
            if CrawledTable.select().count() == 20:
                break
            links = UncrawledTable.select()
            if not links:
                break
            for link in links:
                if CrawledTable.select().count() == 20:
                    break
                if CrawledTable.select().where(CrawledTable.crawledURL == link.uncrawledURL).exists():
                    pass
                else:
                    self.crawl(link.uncrawledURL)
                link.delete_instance()
        CrawledTable.delete().execute()
        UncrawledTable.delete().execute()
        RobotTxts.delete().execute()



    def crawl(self, link):

        robotParser = self.setupRobotParser(link)
        if robotParser.can_fetch("*", link):
            while True:
                try:
                    response = urllib.request.urlopen(link)
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        reqRate = robotParser.request_rate("*")
                        if reqRate is None:
                            return
                        else:
                            time.sleep(reqRate.seconds + 1)
                    else:
                        return

            urlInfo = response.info()
            dataType = urlInfo.get_content_type()
            if 'html' not in dataType:
                return
            returnedLink = response.geturl()
            if returnedLink == link:
                CrawledTable(crawledURL = link).save()
            else:
                CrawledTable(crawledURL=link).save()
                CrawledTable(crawledURL=returnedLink).save()

            webContent = str(response.read())


            if WebPages.select().where(WebPages.pageURL == returnedLink).exists():
                WebPages.update(pageContent = webContent).where(WebPages.pageURL == returnedLink).execute()
            else:
                WebPages(pageURL = returnedLink, pageContent = webContent).save()

            parser = MyHTMLParser(link)
            parser.feed(str(webContent))
            for l in parser.links:
                UncrawledTable(uncrawledURL=l).save()

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