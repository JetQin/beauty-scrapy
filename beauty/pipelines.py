# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import scrapy
import logging
import os,shutil

from beauty.items import BeautyItem 
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

logger = logging.getLogger('beautyLogger')
class CustomImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['images']:
            yield scrapy.Request(url=image_url,meta={'name':item['name']})

    def item_completed(self, results, item, info):
        logger.info('*************download image complete*************')
        settings = get_project_settings()
        store_path = settings.get('IMAGES_STORE')
        destination_folder = os.path.join(store_path,item['name'])
        if not os.path.exists(destination_folder):
           os.mkdir(destination_folder)

        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        for image_path in image_paths:
            image_name = image_path[image_path.find('/')+1:]
            source_path = os.path.join(store_path,image_path)
            destination_path = os.path.join(destination_folder,image_name)
            shutil.move(source_path,destination_path)
            logger.info('*************source path:%s,destination path:%s',source_path,destination_path)
        return item


class ItemPipeline(object):

    def getItem(self,item):
        if type(item) is str:
            return item
        elif type(item) is list and len(item)>0:
            return item[0]
        else:
            return ''

    def process_item(self, item, spider):
        item = BeautyItem(
            name = self.getItem(item['name']),
            avatar = self.getItem(item['avatar']),
            city = self.getItem(item['city']),
            height = self.getItem(item['height']),
            weight = self.getItem(item['weight']),
            details = self.getItem(item['details']),
            telephone = self.getItem(item['telephone']),
            images = item['images']
        )
        return item


class BeautyPipeline(object):

    collection_name = 'mm'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
