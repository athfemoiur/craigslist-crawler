import json
from abc import ABC, abstractmethod

from mongo import MongoDatabase


class AbstractStorage(ABC):
    @abstractmethod
    def store(self, data, *args):
        pass

    @abstractmethod
    def load(self, *args, **kwargs):
        pass


class MongoStorage(AbstractStorage):
    def __init__(self, data_type):
        self.mongo = MongoDatabase()
        self.data_type = data_type

    def store(self, data, *args):
        collection_name = self.data_type
        collection = getattr(self.mongo.database, collection_name)
        if len(data) > 1 and isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)

    def load(self, collection_name, filter_data=None):
        collection = getattr(self.mongo.database, collection_name)
        if filter_data is not None:
            data = collection.find(filter_data)
        else:
            data = collection.find()
        return data

    def update_flag(self, data):
        self.mongo.database.adv_links.find_one_and_update({"_id": data["_id"]},
                                                          {"$set": {"flag": True}})


class FileStorage(AbstractStorage):
    def __init__(self, data_type):
        self.data_type = data_type

    def store(self, data, filename=None):
        if self.data_type == 'adv_links':
            file_path = f"data/{filename}.json"
        else:
            file_path = f"data/adv/{filename}.json"
        with open(file_path, 'w') as f:
            f.write(json.dumps(data))

    @staticmethod
    def load(content):
        with open('data/adv_links.json', 'r') as f:
            links = json.loads(f.read())
            if content == 'lnk':
                links = list(filter(lambda x: x["flag"] is False, links))
            elif content == 'img':
                pass
        return links
