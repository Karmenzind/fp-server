# -*- coding: utf-8 -*-
import json
import time

import scrapy
from scrapy import Request
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from proxy_spider import utils
from proxy_spider.items import Proxy
from proxy_spider.spiders import _BaseSpider


class KuaidailiSpider(_BaseSpider):
    name = 'kuaidaili'
    allowed_domains = ['www.kuaidaili.com']

    def start_requests(self):
        meta = {
            # 'max_retry_times': 10,
            'download_timeout': 20,
        }
        for _type in ('inha', 'intr'):
            for _page in range(1, 100):
                if self.complete_condition():
                    break
                url = 'http://www.kuaidaili.com/free/%s/%s/' % (_type, _page)
                yield Request(url, meta=meta, dont_filter=True)

    def parse(self, response):
        for tr in response.xpath('//table/tbody/tr'):
            ex = tr.xpath('./td/text()').extract()
            ip = ex[0]
            port = ex[1]
            scheme = ex[3].lower()

            if ip and port and scheme in ('http', 'https'):
                yield self.build_check_recipient(ip, port, scheme)
