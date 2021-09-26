import json
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from parser import AdvertisementParser
from config import base_link, default_cities, storage_type, HEADER
from storage import MongoStorage, FileStorage


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

    def store(self, data, *args):
        self.storage.store(data, *args)

    def start(self, store=False):
        for lnk in self.links:
            response = self.get_page(lnk['url'])
            data = self.parser.parse(response.text)
            if store:
                self.store(data, data.get('post_id', 'no id!'))
                if isinstance(self.storage, MongoStorage):
                    self.storage.update_flag(lnk)
                else:
                    lnk["flag"] = True
        if isinstance(self.storage, FileStorage):
            with open('data/adv_links.json', 'w') as f:
                f.write(json.dumps(self.links))


class ImageDownloader(BaseCrawl):
    def __init__(self):
        self.storage = MongoStorage("images")
        self.adv = self.storage.load('adv_data')

    @staticmethod
    def get_image(url):
        try:
            response = requests.get(url, stream=True)
        except requests.HTTPError:
            print('unable to get response')
            return None
        return response

    def store(self, data, adv_id, img_number=None):
        filename = f"{adv_id}-{img_number}"
        self.save_to_disk(data, filename)

    @staticmethod
    def save_to_disk(response, filename):
        with open(f"data/images/{filename}.jpg", 'wb') as f:
            total = response.headers.get("content-length")
            if total is None:
                f.write(response.content)
            else:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)

    def start(self):
        for adv in self.adv:
            counter = 1
            for img in adv["image"]:
                response = self.get_image(img["url"])
                self.store(response, adv["post_id"], counter)
                counter += 1
