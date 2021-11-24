from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread

import requests
from bs4 import BeautifulSoup
from parser import AdvertisementParser
from config import base_link, default_cities, storage_type, HEADER
from storage import MongoStorage, FileStorage
from tasks import download_image


class BaseCrawl(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def store(self, data, filename):
        pass

    @staticmethod
    def get_page(url, headers=HEADER):
        try:
            response = requests.get(url, headers=headers)
        except requests.HTTPError:
            print('unable to get response')
            return None
        return response


class LinkCrawler(BaseCrawl):

    def __init__(self, cities=default_cities, link=base_link):
        self.cities = cities
        self.link = link
        self.storage = MongoStorage('adv_links') if storage_type == 'mongo' else FileStorage('adv_links')

    @staticmethod
    def get_link(html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all('a', attrs={'class': 'hdrlnk'})

    def crawl_city(self, url_init):
        start = 0
        crawl = True
        adv_links = []
        while crawl:
            response = self.get_page(url_init + str(start))
            response_links = self.get_link(response.text)
            if not response_links:
                break
            adv_links.extend([{'url': lnk.get('href'), 'flag': False} for lnk in response_links])
            start += 120

        return adv_links

    def store(self, data, *args):
        self.storage.store(data, *args)

    def start(self):
        adv_links = list()
        for city in self.cities:
            links = self.crawl_city(self.link.format(city))
            print(f"{city} : {len(links)} advertisements")
            adv_links.extend(links)
        self.store(adv_links, 'adv_links')


class DataCrawler(BaseCrawl):
    def __init__(self):
        self.parser = AdvertisementParser()
        self.storage = MongoStorage('adv_data') if storage_type == 'mongo' else FileStorage('adv_data')
        if isinstance(self.storage, MongoStorage):
            self.links = self.storage.load('adv_links', {'flag': False})
        else:
            self.links = self.storage.load('lnk')
        self.queue = self.create_queue()

    def store(self, data, *args):
        self.storage.store(data, *args)

    def create_queue(self):
        queue = Queue()
        for link in self.links:
            queue.put(link)
        return queue

    def crawl(self):
        while True:
            link = self.queue.get()

            response = self.get_page(link['url'])
            data = self.parser.parse(response.text)
            print('data received')
            download_image.delay(data)

            self.store(data, data.get('post_id', 'no id!'))
            if isinstance(self.storage, MongoStorage):
                self.storage.update_flag(link)
            self.queue.task_done()
            if self.queue.empty():
                break

    def start(self):
        for _ in range(10):
            thread = Thread(target=self.crawl)
            thread.start()
        self.queue.join()
