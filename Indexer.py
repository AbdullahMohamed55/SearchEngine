class Indexer:

    def __init__(self):
        pass #to be stored in database
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


'''
test = Indexer()

test.addToIndex("google","http://www.google.com")
test.addToIndex("google","http://www.xxx.com")
test.addToIndex("Google","http://www.xxx.com")
print (test.lookup("google"))
print (test.lookup("Google"))
print (test.lookup("gooogle"))


print (test.index)
'''