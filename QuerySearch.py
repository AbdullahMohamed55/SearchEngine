from nltk.stem.porter import *
from Model import PageRank, IndexerTable

class Query:
    def __init__(self, query):
        self.rankResults = {} #url:score

        # input validation & stemming

        self.query, self.isPhrase = self._parseQuery(query)

        if self.isPhrase:
            self.phraseSearch()
        else:
            self.queryStem = [PorterStemmer().stem(x) for x in self.query]
            self.textSearch()
        pass

    def _parseQuery(self, query):

        query = str(query).strip()
        # phrase if "text"
        isPhrase = True if (re.findall('"([^"]*)"', query)) else False
        pattern = re.compile(r'[\W_]+')
        query = pattern.sub(' ', query).lower()

        return query.split(), isPhrase

    def textSearch(self):
        for x, word in enumerate(self.query):
            exact, stem  = self._wordLookUp(word, self.queryStem[x])
            print(exact,stem)
            #freq.
            ...

    def _frequencyScore(self, count):
        return count * 0.5

    def _importanceScore(self, imp):
        if imp == 0 :
            return 4.
        elif imp == 1:
            return 2.
        else:
            return 1.

    def _relevanceScore(self, isExact): #stem or exact
        if isExact:
            return 2.
        else:
            return 1.
        pass
    def _pagePopularityScore(self, pageVisits):
        return pageVisits * 2

    def getPageRanks(self,urls):
        ...

    def _wordLookUp(self,word,stem):
        while True:
            try:
                #exact word
                exactResult = {}
                resultQuery = IndexerTable.select().where(IndexerTable.keyword == word)
                if(resultQuery.exists()):
                    for entry in resultQuery:
                        exactResult.update({'url': entry.url , 'pos': entry.positons, 'imp': entry.importance })
                break
            except:
                print('SEARCHer: Database busy, retrying.')

        while True:
            try:
                #stem search
                stemResult = {}
                resultQuery = IndexerTable.select().where(IndexerTable.stem == stem and IndexerTable.keyword != word)
                if (resultQuery.exists()):
                    for entry in resultQuery:
                        stemResult.update({'url': entry.url , 'pos': entry.positons, 'imp': entry.importance })
                break
            except:
                print('SEARCHer: Database busy, retrying.')

        return exactResult, stemResult

    #TODO phrase search
    def phraseSearch(self):
        ...

    #TODO query suggestion
    def addSuggestion(self):
        ...
    def getSuggestion(self):
        ...




'''
test = Query('the chatting cat')
print(test.query)
print(test.isPhrase)
print(test.queryStem)
'''