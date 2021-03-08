import sys

from crawl import LinkCrawler, DataCrawler, ImageDownloader

if __name__ == '__main__':
    switch = sys.argv[1]
    if switch == 'links':
        crawler_l = LinkCrawler()
        crawler_l.start()
    elif switch == 'data':
        crawler_d = DataCrawler()
        crawler_d.start(store=True)
    elif switch == 'image':
        crawler_img = ImageDownloader()
        crawler_img.start()
