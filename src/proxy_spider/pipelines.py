# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

from proxy_spider.items import Proxy
from service.proxy.proxy import blocking_proxy_srv
from utils.tools import subdict


class PersistencePipeline:
    def __init__(self):
        self.srv = blocking_proxy_srv
        self.cli = self.srv.cli

    def process_item(self, item, spider):
        if item and isinstance(item, Proxy):
            try:
                self.delete_existed(item, spider)
                key = self.srv.save_proxy(item)
                spider.logger.debug('Stored: %s' % key)
            except:
                spider.logger.exception("Item: %s" % item)
        return item

    def delete_existed(self, item, spider):
        _f = subdict(item, ['ip', 'port', 'scheme'])
        for k in self.srv.keys_by_dict(_f):
            self.srv.delete(k)
            spider.logger.debug('Deleted: %s' % k)
