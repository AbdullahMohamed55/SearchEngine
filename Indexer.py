import re
from Model import *
import urllib.request
from bs4 import BeautifulSoup
from bs4 import Comment
from nltk.corpus import stopwords
from nltk.stem.porter import *
import timeit

class Indexer:

    def __init__(self):
        pass

    def update(self,url,content):

        #delete old entries of this url (if exists any)
        self._deleteOldEntries(url)

        #parse the webpage content
        wordIndexes, wordImportance = self.parser(content)

        for word in wordImportance:
            if (word in wordIndexes):
                print(word, wordIndexes[word], wordImportance[word])
                print(self._addToIndex(word, url, wordIndexes[word], wordImportance[word]))



    def _deleteOldEntries(self,url):

        query = IndexerTable.delete().where(IndexerTable.url == url)
        print("deleted ", query.execute(), "entries.")


    # inserts a new entry(keyword,url)
    def _addToIndex(self, keyword, url, pos = [], importance = 2):

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

    def _indexFile(self,wordList):
        fileIndex = {}
        # input = [word1, word2, ...]
        # output = {word1: [pos1, pos2], word2: [pos2, pos3], ...}
        for index, word in enumerate(wordList):
            if word in fileIndex.keys():
                fileIndex[word].append(index)
            else:
                fileIndex[word] = [index]
        return fileIndex


    def _assignImportance(self,keywords,count,imp,importanceMap = {}):

        for word in keywords:
            if not (word in importanceMap):
                importanceMap[word]= imp
                count+=1

    def _visibleText(self,element):  # removing text in script and comment

        if element.parent.name in ['style', 'script', 'link', '[document]']:
            return False

        elif re.match('.*<!--.*-->.*', str(element)):
            return False
        return True

    def _parseKeywords(self,text):

        for i in range(len(text)):

            pattern = re.compile('[\W_]+')
            text[i] = pattern.sub(' ', text[i])
            re.sub(r'[\W_]+', '', text[i])
            text[i] = text[i].lower()
            text += text[i].split()
            text[i] = None

        return text

    def _removeStopWords(self,wordList):

        stop = set(stopwords.words('english'))
        wordList = [word for word in wordList if word not in stop and len(word) > 2]
        return wordList


    def _initParser(self,text):


        soup = BeautifulSoup(text, 'html.parser')

        # ---------------Finding Comments to remove them---------------
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]

        # ---------------Getting Text without Comments-------------------
        texts = soup.find_all(text=True)


        # ---------------removing the unwanted script and links from the doc and returning list of words------------
        visible_texts = filter(self._visibleText, texts)

        # ---------------remove all symbols like #$%@ , spaces and newlines--------------

        parsedWords = self._parseKeywords(list(visible_texts))
        parsedWords = [word for word in parsedWords if word is not ' ' and word is not None]
        # remove stop words
        parsedWords = self._removeStopWords(parsedWords)

        # stemming words
        pass #NOW??
        '''
        stemmer = PorterStemmer()
        for i in range(len(parsedWords)):
            parsedWords[i] = stemmer.stem(parsedWords[i])
        '''
        return parsedWords

    def parser(self, htmlDoc): #this function works on a html doc


        soup = BeautifulSoup(htmlDoc, 'html.parser')
        count = 0
        importMap ={}

        #-----------------parsing Title and assigning its importance map----------------
        if(soup.title.string is not None):
            title = self._initParser(str(soup.title))

        self._assignImportance(title,count,0,importMap)

        #parsing headers
        headers = [soup.h1 , soup.h2 , soup.h3 , soup.h4
                       , soup.h5 , soup.h6]

        headers = [str(x) for x in headers if x is not None]
        headers = self._initParser(' '.join(headers))
        self._assignImportance(headers, count, 1, importMap)


        #---------------------parsing  plain text---------------------
        plainText = self._initParser(htmlDoc)
        self._assignImportance(plainText,count,2,importMap)

        # --------------indexing words -------------
        indexMap = self._indexFile(plainText)


        return indexMap,importMap
