# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import logging


class CtripFlightsPipeline:
    def process_item(self, item, spider):
        return item


class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.client = None
        self.db = None
        self.collection = None
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'test'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION', 'flights')
        )

    def open_spider(self, spider):
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            self.collection = self.db[self.mongo_collection]
            self.logger.info(f"成功连接到MongoDB: {self.mongo_uri}")
            self.logger.info(f"使用数据库: {self.mongo_db}")
            self.logger.info(f"使用集合: {self.mongo_collection}")
        except Exception as e:
            self.logger.error(f"连接MongoDB时出错: {e}")
            raise e

    def close_spider(self, spider):
        if self.client:
            self.client.close()
            self.logger.info("已关闭MongoDB连接")

    def process_item(self, item, spider):
        try:
            # 将item转换为字典
            item_dict = dict(item)
            self.logger.info(f"正在保存航班数据，ID: {item_dict.get('_id')}")
            
            # 插入数据
            result = self.collection.insert_one(item_dict)
            self.logger.info(f"成功保存航班数据，MongoDB ID: {result.inserted_id}")
            
            # 打印一些数据用于调试
            self.logger.info(f"保存的数据包含 {len(item_dict.get('data', {}).get('flightLists', []))} 个航班")
            
        except Exception as e:
            self.logger.error(f"保存到MongoDB时出错: {e}")
            self.logger.error(f"错误详情: {str(e)}")
        return item
