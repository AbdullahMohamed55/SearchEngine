import Crawler

SEED_PATH = 'seeds.txt'
DOWNLOAD_PATH = './pages/'

crawlerObj = Crawler.Crawler(SEED_PATH, DOWNLOAD_PATH)
crawlerObj.start()
