import sys

from crawl import LinkCrawler, DataCrawler

if __name__ == '__main__':
    switch = sys.argv[1]
    if switch == 'links':
        crawler_l = LinkCrawler()
        crawler_l.start()
    elif switch == 'data':
        crawler_d = DataCrawler()
        crawler_d.start()
