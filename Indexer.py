import re
from Model import *


class Indexer:

    def __init__(self):
        pass

    #inserts a new entry(keyword,url)
    def addToIndex(self, keyword, url, pos = [], importance = 0):

        try:

            IndexerTable.create(keyword= keyword , url = url, positions = pos, importance = importance).update()

        except IntegrityError: #keyword & url already exists!

            return -1

        return 1

    # returns dic[keyword]->[urls] of searched word(s) or -1
    pass
    def lookupWithWords(self, keywords = []):

        result = {}

        for word in keywords:
            urlList = []
            try:
                resultQuery = IndexerTable.select(IndexerTable.url).where(IndexerTable.keyword == word)
                for x in resultQuery:
                    urlList.append(x.url)

            except IndexerTable.DoesNotExist:
                urlList.append(-1)

            result.update({word: urlList})

        return result

    #maybe we won't need it!
    def lookupWithPages(self, pages=[]):

        result = {}

        for pg in pages:
            wordList = []
            try:
                resultQuery = IndexerTable.select(IndexerTable.keyword).where(IndexerTable.url == pg)
                for x in resultQuery:
                    wordList.append(x.keyword)

            except IndexerTable.DoesNotExist:
                wordList.append(-1)

            result.update({pg: wordList})

        return result

    #deprecated
    def addPageToIndex(self, pageUrl):
        pass #parse html text and extract its content
        content = ""
        pass #split according to!
        words = content.split()
        for word in words:
            self.addToIndex(word, pageUrl)



    def parseKeywords(self,Urls):
        file_to_terms = {}
        for url in Urls:
            pattern = re.compile('[\W_]+')
            file_to_terms[url] = open(url, 'r').read().lower()
            file_to_terms[url] = pattern.sub(' ',file_to_terms[url])
            re.sub(r'[\W_]+','', file_to_terms[url])
            file_to_terms[url] = file_to_terms[url].split()

            #TODO
            pass #if keyword is in the file more than once!
            pass #extract keyword postion(s) in the file via .find() on original file (python list)
            pass #keyword importance (title, header , plaintext) (int)

            for keyword in file_to_terms[url]:
                self.addToIndex(keyword, url) #TODO pass also position and importance
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

print (test.lookup("google"))
print (test.lookup("Google"))
print (test.lookup("gooogle"))


print (test.index)
'''
'''
DB.connect()
#DB.create_tables([IndexerTable])
test = Indexer()
z = test.addToIndex("google","http://www.googlexx.com")
xx = IndexerTable.get(IndexerTable.keyword == 'google')
print(xx.url)
print(z)

search = test.lookup("gooqgle")
print(search)
'''