# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from service.proxy.proxy import blocking_proxy_srv
from scrapy.exceptions import DropItem
from proxy_spider.items import Proxy


class PersistencePipeline:
    def __init__(self):
        self.srv = blocking_proxy_srv
        self.cli = self.srv.cli

    def process_item(self, item, spider):
        if not item:
            raise DropItem('Dropped empty.')

        if isinstance(item, Proxy):
            logger = spider.logger
            try:
                self.srv.new_proxy(item)
                logger.debug('Stored: %s' % item)
            except:
                logger.exception("Item: %s" % item)

        return item
