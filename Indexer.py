import re
class Indexer:

    def __init__(self):
        pass   #to be stored in database
        self.index = {}

    #adds url to index[keyword]
    def addToIndex(self, keyword, url):

        #check if keyword already exists
        if keyword in self.index:
            self.index[keyword].append(url)
            return

        # not found, add new keyword to index
        self.index.update({keyword : [url]})


    def addPageToIndex(self, pageUrl):
        pass #parse html text and extract its content
        content = ""
        pass #split according to!
        words = content.split()
        for word in words:
            self.addToIndex(word, pageUrl)


    #returns list of urls of searched keyword or none
    def lookup(self, keyword):

        if keyword in self.index:

            return self.index[keyword]

        return None

    def parseKeywords(self,Urls):
        file_to_terms = {}
        for url in Urls:
            pattern = re.compile('[\W_]+')
            file_to_terms[url] = open(url, 'r').read().lower()
            file_to_terms[url] = pattern.sub(' ',file_to_terms[url])
            re.sub(r'[\W_]+','', file_to_terms[url])
            file_to_terms[url] = file_to_terms[url].split()
            for keyword in file_to_terms[url]:
                self.addToIndex(keyword, url)
'''
text =
pattern = re.compile('[\W_]+')
text = pattern.sub(' ',text)
print (text)
print (re.sub(r'[\W_]+','', text))
text = text.split()
print (text)



test = Indexer()

test.addToIndex("google","http://www.google.com")
test.addToIndex("google","http://www.xxx.com")
test.addToIndex("Google","http://www.xxx.com")
print (test.lookup("google"))
print (test.lookup("Google"))
print (test.lookup("gooogle"))


print (test.index)
'''
