# -*- coding: utf-8 -*-
from scrapy import Request

from proxy_spider.spiders import _BaseSpider
from utils.collections import shuffled_range


class IhuanSpider(_BaseSpider):
    name = 'ihuan'
    allowed_domains = ['www.ihuan.com']

    def start_requests(self):
        # pages = shuffled_range(1, 100)

        for _page in range(1, 100):
            if self.complete_condition():
                break

            url = 'https://ip.ihuan.me/?page=%s' % _page
            yield Request(url, dont_filter=True)

    def parse(self, response):
        for tr in response.xpath('//table/tbody/tr'):
            ex = tr.xpath('./td//text()').extract()
            ip = ex[0]
            port = ex[1]
            scheme = ['http', 'https'][ex[5] == '支持']
            print(ip, port, scheme)

            if ip and port and scheme in ('http', 'https'):
                yield self.build_check_recipient(ip, port, scheme)
