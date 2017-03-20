import re
from Model import *
from bs4 import BeautifulSoup
import string
import timeit

class Indexer:

    def __init__(self):
        pass

    def deleteOldEntries(self,url):

        query = IndexerTable.delete().where(IndexerTable.url == url)
        print("deleted ", query.execute(), "entries.")


    # inserts a new entry(keyword,url)
    def addToIndex(self, keyword, url, pos = [], importance = 2):

        try:

            IndexerTable.create(keyword= keyword , url = url, positions = pos, importance = importance).update()

        except IntegrityError: # keyword & url already exists!

            return -1

        return 1

    # returns dic[keyword]->[urls] of searched word(s) or -1
    pass

    #for searching
    '''IN: list of keywords OUT: dict[keyword] of urls'''
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


    '''IN: list of urls OUT: dict[url] of keywords'''
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

    '''Parsing functions'''

    def indexFile(self,word_list):
        fileIndex = {}
        # input = [word1, word2, ...]
        # output = {word1: [pos1, pos2], word2: [pos2, pos3], ...}
        for index, word in enumerate(word_list):
            if word in fileIndex.keys():
                fileIndex[word].append(index)
            else:
                fileIndex[word] = [index]
        return fileIndex


    def assignImportance(self,keywords,count,imp,importance_map = {}):

        for word in keywords:
            if not (word in importance_map):
                importance_map[word]= imp
                count+=1


    def removeStopWords(self,s):
        # remove leading and trailing whitespace
        s = s.strip()
        # remove punctuation in the string
        s = s.strip(string.punctuation)
        # remove unwanted words
        return ' '.join(s.split())


    def parseKeywords(self,Text):
        Text = self.removeStopWords(Text)
        pattern = re.compile('[\W_]+')
        Text = pattern.sub(' ', Text)
        re.sub(r'[\W_]+', '', Text)
        return Text.split()


    def parser(self,url,html_doc):

        soup = BeautifulSoup(html_doc, 'html.parser')
        html_doc = soup.get_text().lower()
        count = 0
        import_map = {}
        if(soup.title.string is not None):
            title_keys = self.parseKeywords(soup.title.string.lower())
            self.assignImportance(title_keys,count,0,import_map)
        headers_keys = [soup.h1 , soup.h2 , soup.h3 , soup.h4
                       , soup.h5 , soup.h6]

        headers_keys = [x.string.lower() for x in headers_keys if x is not None]
        headers_keys = self.parseKeywords(''.join(headers_keys))
        self.assignImportance(headers_keys,count,1,import_map)
        html_doc = self.parseKeywords(html_doc)
        self.assignImportance(html_doc,count,2,import_map)

        indexMap = self.indexFile(self.parseKeywords(' '.join(html_doc)))

        pass
        self.deleteOldEntries(url)

        for word in import_map:
            if(word in indexMap):
                print(word,indexMap[word],import_map[word])
                print(self.addToIndex(word,url,indexMap[word],import_map[word]))
        print(len(indexMap))

        #return import_map,self.indexFile(self.parseKeywords(' '.join(html_doc)))


'''
file = open("hi.html",'r').read().lower()
indexer = Indexer()
indexer.parser("http://www.testxx.com",file)
#print(import_map)
#print (pos_map)
'''
'''
file = open(,'wb')
parser = MyHTMLParser()
parser.feed(file)
print (parser.imp_map)

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


'''def parseKeywordsTry(self, Urls):  # this func is not used
    file_to_terms = {}
    for url in Urls:

        pattern = re.compile('[\W_]+')
        file_to_terms[url] = open(url, 'r').read().lower()
        file_to_terms[url] = pattern.sub(' ', file_to_terms[url])
        re.sub(r'[\W_]+', '', file_to_terms[url])
        file_to_terms[url] = file_to_terms[url].split()

        # TODO
        pass  # if keyword is in the file more than once!
        pass  # extract keyword postion(s) in the file via .find() on original file (python list)
        ''' '''Done using func indexFile if the word occur more than once the
        first word only will be recorded . the title and header will be in first of the file
        ''''''
        pass  # keyword importance (title, header , plaintext) (int)

        for keyword in file_to_terms[url]:
            self.addToIndex(keyword, url)  # TODO pass also position and importance
'''