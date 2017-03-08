from Model import *
from Indexer import Indexer


DB.connect()

"""RUN this only once when creating table!"""
#DB.create_tables([IndexerTable])

test = Indexer()

zidan = test.addToIndex("zidan","http://www.ZidanMusk.com")
osmium = test.addToIndex("osmium","http://www.Osmium.com")
abdo = test.addToIndex("abdo","http://www.Abdo.com")

words = ["zidan","osmium", "abdo","musk"]
searchW = test.lookupWithWords(words)

pages = ["http://www.ZidanMusk.com","http://www.Osmium.com","http://www.Abdo.comNOOO"]
searchP = test.lookupWithPages(pages)

print(searchW)
print(searchP)

DB.close()