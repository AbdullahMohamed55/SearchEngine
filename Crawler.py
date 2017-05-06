import sqlite3
import threading
from Model import *
import urllib.parse
import urllib.request
from datetime import *
from time import sleep
import urllib.response
import urllib.robotparser
from html.parser import HTMLParser

#Number of pages to crawl for per run.
NUMOFPAGES = 1000000

class Crawler(threading.Thread):

    numberOfThreads = 0
    webpagesSaved = 0
    dbLock = threading.Lock()
    webpagesLock = threading.Lock()
    linksLock = threading.Lock()
    listOfLinks = []
    assignedLock = threading.Lock()
    assignedList = []

    def __init__(self, cID):

        try:
            threading.Thread.__init__(self)
            self.crawlerID = cID
            for seed in Seeds.select():
                if UncrawledTable.select().where(UncrawledTable.uncrawledURL == seed.pageURL).exists():
                    continue

                timeDifference = datetime.now() - seed.lastCrawl
                timeDifferenceInHours = timeDifference.days * 24 + timeDifference.seconds // 3600
                pass #for quick testing
                #timeDifferenceInHours = 100
                if timeDifferenceInHours >= seed.crawlFrequency:
                    UncrawledTable.get_or_create(uncrawledURL = seed.pageURL)
                    seed.lastCrawl = datetime.now()
                    seed.save()
        except (OperationalError, sqlite3.OperationalError):
            print("Database already open by something")


    def run(self):

            tryTwice = 0

            while True:
                try:

                    print('Thread ' + str(self.crawlerID) + ': Getting link.')
                    Crawler.webpagesLock.acquire()
                    if Crawler.webpagesSaved >= NUMOFPAGES:
                        print('Thread ' + str(self.crawlerID) + ': Target reached, ending crawl')
                        Crawler.webpagesLock.release()
                        break
                    Crawler.webpagesLock.release()
                    exists = None
                    while True:
                        try:
                            linkQuery = UncrawledTable.select().limit(1)  # just to check if table is empty #rawshana
                            exists = linkQuery.exists()
                            break


                        except (OperationalError, sqlite3.OperationalError) as e:
                            if 'binding' in str(e):
                                break
                            print('Thread ', self.crawlerID, ': Database busy, retrying.')
                        except:
                            break

                    if not exists:
                        #if table is empty

                        if tryTwice == 2:
                            print('Thread ' + str(self.crawlerID) + ': No links available. Ending crawl.')
                            break
                        print('Thread ' + str(self.crawlerID) + ': No links available. Sleeping for 60 seconds. Attempt: ' + str(tryTwice + 1))
                        sleep(60)
                        tryTwice = tryTwice + 1
                        continue
                    tryTwice = 0

                    link = self._getALink()
                    ### i am here
                    if link == 'ALLLINKSASSIGNED':
                        #if table is empty

                        print('Thread ' + str(self.crawlerID) + ': All links assigned.')
                        sleep(1)
                        continue

                    x = None
                    while True:
                        try:
                            x = CrawledTable.select().where(CrawledTable.crawledURL == link).exists()
                            break
                        except (OperationalError, sqlite3.OperationalError) as e:
                            if 'binding' in str(e):
                                break
                            print('Thread ', self.crawlerID, ': Database busy, retrying.')
                        except:
                            break

                    if x: #if link already exists in CrawledTable
                        print('Thread ' + str(self.crawlerID) + ': Link already visited.' + ' ' + link)


                        #increment this page rank
                        while True:
                            try:
                                selectQuery = PageRank.select().where(PageRank.pageURL == link)
                                if (selectQuery.exists()):
                                    PageRank.update(pageInLinks = PageRank.pageInLinks + 1).where(
                                        PageRank.pageURL == link).execute()

                                break
                            except (OperationalError, sqlite3.OperationalError) as e:
                                if 'binding' in str(e):
                                    break
                                print('Thread ', self.crawlerID, ': Database busy, retrying.')
                            except:
                                break


                        Crawler.linksLock.acquire()
                        Crawler.assignedLock.acquire()
                        Crawler.assignedList.remove(link)
                        try:
                            Crawler.listOfLinks.remove(link)
                        except:
                            pass
                        Crawler.assignedLock.release()
                        Crawler.linksLock.release()

                        while True:
                            try:
                                UncrawledTable.delete().where(UncrawledTable.uncrawledURL == link).execute()
                                break
                            except (OperationalError, sqlite3.OperationalError) as e:
                                if 'binding' in str(e):
                                    break
                                print('Thread ', self.crawlerID, ': Database busy, retrying.')
                            except:
                                break

                        continue

                    Crawler.webpagesLock.acquire()

                    while True:
                        try:
                            print("CRAWLED URLS = ", CrawledTable.select().count(), ' Thread ' + str(self.crawlerID))
                            break
                        except (OperationalError, sqlite3.OperationalError)as e:
                            if 'binding' in str(e):
                                break
                            print('Thread ', self.crawlerID, ': Database busy, retrying.')
                        except:
                            break


                    print("Actual pages = ", Crawler.webpagesSaved, ' Thread ' + str(self.crawlerID))
                    Crawler.webpagesLock.release()
                    print('Thread ' + str(self.crawlerID) + ': Done getting link.')
                    print('Thread ' + str(self.crawlerID) + ': Crawling link: ' + link)

                    self.crawl(link)

                    while True:
                        try:
                            UncrawledTable.delete().where(UncrawledTable.uncrawledURL == link).execute()
                            break
                        except (OperationalError, sqlite3.OperationalError) as e:
                            if 'binding' in str(e):
                                break
                            print('Thread ', self.crawlerID, ': Database busy, retrying.')
                            sleep(1)
                            pass
                        except:
                            break

                    Crawler.linksLock.acquire()
                    Crawler.assignedLock.acquire()
                    Crawler.assignedList.remove(link)
                    try:
                        Crawler.listOfLinks.remove(link)
                    except:
                        pass
                    Crawler.assignedLock.release()
                    Crawler.linksLock.release()

                    while True:
                        try:
                            CrawledTable.create(crawledURL=link).update()
                            break
                        except (OperationalError, sqlite3.OperationalError) as e:
                            if 'binding' in str(e):
                                break
                            print('Thread ', self.crawlerID, ': Database busy, retrying.')
                            sleep(1)
                            pass
                        except:
                            break

                    print('Thread ' + str(self.crawlerID) + ': Done crawling link: ' + link)

                # Just in case, but these 2 exceptions should never happen
                except IntegrityError:
                    print("IntegrityError has occurred by thread " + str(self.crawlerID) + " !")
                except (OperationalError, sqlite3.OperationalError):
                    print("DatabaseError: DB is locked while thread " + str(self.crawlerID) + " tried to access it!")

            print("Thread:", self.crawlerID, "is Exiting...")


    def _getALink(self):
        Crawler.linksLock.acquire()
        Crawler.assignedLock.acquire()
        listOfLinksQuery = None
        if len(Crawler.listOfLinks) == 0:

            while True:
                try:
                    listOfLinksQuery = UncrawledTable.select().limit(Crawler.numberOfThreads)

                    break
                except (OperationalError, sqlite3.OperationalError) as e:
                        if 'binding' in str(e):
                            break
                        print('Thread ', self.crawlerID, ': Database busy, retrying.')
                except:
                    break

            while True:
                try:
                    for link in listOfLinksQuery:
                        Crawler.listOfLinks.append(link.uncrawledURL)
                    break
                except (OperationalError, sqlite3.OperationalError) as e:
                    if 'binding' in str(e):
                        break
                    print('Thread ', self.crawlerID, ': Database busy, retrying.')
                except:
                    break

        if len(Crawler.listOfLinks) == 0:
            retVal = "ALLLINKSASSIGNED"
        else:
            retVal = Crawler.listOfLinks.pop()

        acquired = False
        breaked = False

        while True:
            if retVal not in Crawler.assignedList:
                break
            if len(Crawler.listOfLinks) == 0:
                if acquired == True:
                    breaked = True
                    break
                acquired = True

                while True:
                    try:
                        listOfLinksQuery = UncrawledTable.select().limit(Crawler.numberOfThreads)
                        break
                    except (OperationalError, sqlite3.OperationalError)as e:
                        if 'binding' in str(e):
                            break
                        print('Thread ', self.crawlerID, ': Database busy, retrying.')
                    except:
                        break

                while True:
                    try:
                        for link in listOfLinksQuery:
                            Crawler.listOfLinks.append(link.uncrawledURL)
                        break
                    except (OperationalError, sqlite3.OperationalError) as e:
                        if 'binding' in str(e):
                            break
                        print('Thread ', self.crawlerID, ': Database busy, retrying.')
                    except:
                        break

            if len(Crawler.listOfLinks) == 0:
                retVal = "ALLLINKSASSIGNED"
            else:
                retVal = Crawler.listOfLinks.pop()

        if breaked:
            Crawler.assignedLock.release()
            Crawler.linksLock.release()
            return 'ALLLINKSASSIGNED'
        else:
            Crawler.assignedList.append(retVal)
            Crawler.assignedLock.release()
            Crawler.linksLock.release()
            return retVal


    def crawl(self, link):

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
                        sleep(120)
                        tryOnce = 1
                    else:
                        return
                # for handling any other url errors
                except:
                    print('Error opening link: ',link, " by thread : ", self.crawlerID)

                    return

            returnedLink = response.geturl()
            if returnedLink != link:
                print('Thread ' + str(self.crawlerID) + ': Redirection:' + link + ' to ' + returnedLink + ' returning.')
                return

            urlInfo = response.info()
            dataType = urlInfo.get_content_type()
            if 'html' not in dataType:
                print('Thread ' + str(self.crawlerID) + ': Not HTML ' + link + ' returning.')
                return

            try:
                webContent = response.read().decode(response.headers.get_content_charset('utf-8'))
            except:
                print("Incomplete Read of web content due to a defective http server.")
                webContent = None

            if(webContent):
                Crawler.webpagesLock.acquire()
                if Crawler.webpagesSaved < NUMOFPAGES:
                    Crawler.webpagesSaved += 1
                else:
                    print('Thread ' + str(self.crawlerID) + ': Page number limit reached ')
                    Crawler.webpagesLock.release()
                    return
                Crawler.webpagesLock.release()
                selector = None
                while True:
                    try:
                        selector = WebPages.select().where(WebPages.pageURL == returnedLink).exists()
                        break
                    except (OperationalError , sqlite3.OperationalError) as e:
                        if 'binding' in str(e):
                            break
                        print('Thread ', self.crawlerID, ': Database busy, retrying.')
                    except:
                        break

                if selector:
                    print('Thread ' + str(self.crawlerID) + ': Updating webpage ' + link)

                    while True:
                        try:
                            WebPages.update(pageContent=webContent).where(
                                WebPages.pageURL == returnedLink).execute()
                            break
                        except (OperationalError, sqlite3.OperationalError) as e:
                            if 'binding' in str(e):
                                break
                            print('Thread ', self.crawlerID, ': Database busy, retrying.')
                        except:
                            break

                else:
                    print('Thread ' + str(self.crawlerID) + ': Saving webpage ' + link )
                    try:
                        inserted = False
                        while True:
                            try:
                                if not inserted:
                                    WebPages(pageURL=returnedLink, pageContent=webContent).save()
                                    inserted =  True
                                ...
                                PageRank.create(pageURL=returnedLink).update()
                                ...
                                break
                            except (OperationalError, sqlite3.OperationalError) as e:
                                if 'binding' in str(e):
                                    break
                                print('Thread ', self.crawlerID, ': Database busy, retrying.')
                            except:
                                break
                    #should never happen
                    except:
                        print('UnexpectedException: In saving webpage WEEEEEEEEEEEEEEEEEEEEEEE')

                print('Thread ' + str(self.crawlerID) + ': Done saving webpage and starting link extraction ' + link)
                try:
                    parser = MyHTMLParser(link)
                    parser.feed(str(webContent))
                #should never happen
                except:
                    print('UnexpectedException: in parser WEEEEEEEEEEEEEEEEEEEEEEE')

                size = 999
                while True:
                    try:
                        for i in range(0, len(parser.links), size):
                            UncrawledTable.insert_many(parser.links[i:i + size]).upsert().execute()
                        break
                    except (OperationalError, sqlite3.OperationalError) as e:
                        if 'binding' in str(e):
                            break
                        print('Thread ', self.crawlerID, ': Database busy, retrying.')
                    except:
                        break

                while True:
                    try:
                        print("UNCRAWLED URLS = ", UncrawledTable.select().count(), ' Thread ' + str(self.crawlerID))
                        break
                    except (OperationalError, sqlite3.OperationalError) as e:
                        if 'binding' in str(e):
                            break
                        print('Thread ', self.crawlerID, ': Database busy, retrying.')
                    except:
                        break

                print('Thread ' + str(self.crawlerID) + ': Done inserting links ' + link)


    def setupRobotParser(self, url):

        rp = urllib.robotparser.RobotFileParser()
        robotData = None
        currentUrlComponents = urllib.parse.urlparse(url)
        robotLocation = urllib.parse.urljoin(currentUrlComponents.scheme + '://' + currentUrlComponents.netloc, 'robots.txt')

        while True:
            try:
                robotQuery = RobotTxts.select().where(RobotTxts.netLoc == robotLocation)
                if (robotQuery.exists()):
                    robotData = robotQuery.get()
                break
            except (OperationalError, sqlite3.OperationalError) as e:
                if 'binding' in str(e):
                    break
                print('Thread ', self.crawlerID, ': Database busy, retrying.')
            except:
                break

        if robotData:
            rp.parse(str(robotData.robotContent))
        else:
            try:
                robotContentFromInternet = str(urllib.request.urlopen(robotLocation).read())
            except:
                robotContentFromInternet = ''

            rp.parse(robotContentFromInternet)

            while True:
                try:
                    RobotTxts(netLoc=robotLocation, robotContent=robotContentFromInternet).save()
                    break
                except (OperationalError, sqlite3.OperationalError) as e:
                    if 'binding' in str(e):
                        break
                    print('Thread ', self.crawlerID, ': Database busy, retrying.')
                    sleep(1)
                    pass
                except:
                    break

        return rp


'''---------------------------------------------HTML Parser----------------------------------------------------------'''

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
                    # check if not none
                    if(link):
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
                        '''this option lets us crawl deeper into the current host'''
                        #link = urllib.parse.urljoin(parsedLink.scheme + '://' + parsedLink.netloc, parsedLink.path)
                        '''this option only lets us crawl the main pages of the hosts'''
                        link = parsedLink.scheme + '://' + parsedLink.netloc
                        if link[-1] != '/':
                            link = link + '/'
                        self.links.append({'uncrawledURL': link})
