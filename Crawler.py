import urllib.request
import urllib.response
from HTMLParser import HTMLParser


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    file = open('links.txt', 'w')
                    file.write(value)
                    file.write("\n")
                    file.close()



class Crawler:
    def getPage(url):
        response = urllib.request.urlopen(url)
        webcontent = response.read()
        f = open('page.html', 'wb')
        f.write(webcontent)
        f.close()

    def readPages(self):


    def searchUrls(page):
        parser = MyHTMLParser()
        parser.feed(page)

    def getAllUrls(url):
        while True:
            url ,endpos = getPage
