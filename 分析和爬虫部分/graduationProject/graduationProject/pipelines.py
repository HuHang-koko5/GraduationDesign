# -*- coding: utf-8 -*-
import pymongo
from pymongo.errors import DuplicateKeyError
from graduationProject.items import SinaItem
from graduationProject.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MongoDBPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = client[DB_NAME]

    def process_item(self, item, spider):
        if isinstance(item, SinaItem):
            # table_name = 'why'
            table_name = item['key_time']+'--'+item['key_word']
            col = self.db[table_name]
            self.insert_item(col, item)
            # return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            pass