import urllib.request
import urllib.response
import urllib.parse
import urllib.robotparser
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self, currentLink):
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
                    self.links.append(link)

class Crawler:
    def __init__(self, seedPath, dlPath):
        self.downloadPath = dlPath
        self.linksToVisit = []
        self.visitedLinks = []
        seedFile = open(seedPath, 'r')
        for line in seedFile.readlines():
            self.linksToVisit.append(line)
        seedFile.close()

    def start(self):
        while (self.linksToVisit) and (len(self.visitedLinks) < 20):
            link = self.linksToVisit.pop()
            if link not in self.visitedLinks:
                self.crawl(link)
            self.visitedLinks.append(link)

    def crawl(self, link):
        self.currentUrlComponents = urllib.parse.urlparse(link)
        robotParser = self.setupRobotParser(link)
        if robotParser.can_fetch("*", link):
            response = urllib.request.urlopen(link)
            urlInfo = response.info()
            dataType = urlInfo.get_content_type()
            if 'html' not in dataType:
                return
            returnedLink = response.geturl()
            if returnedLink == link:
                self.visitedLinks.append(link)
            else:
                self.visitedLinks.append(link)
                self.visitedLinks.append(returnedLink)

            webContent = response.read().decode('utf-8')
            fileWritePath = self.downloadPath + link
            if fileWritePath.endswith('/'):
                fileWritePath += 'index.html'
            f = open(fileWritePath, 'wb')
            f.write(webContent)
            f.close()
            parser = MyHTMLParser(link)
            parser.feed(webContent)
            self.linksToVisit.append(parser.links)

    def setupRobotParser(self, url):
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urllib.parse.urljoin(self.currentUrlComponents.netloc, 'robots.txt'))
        rp.read()

        return rp