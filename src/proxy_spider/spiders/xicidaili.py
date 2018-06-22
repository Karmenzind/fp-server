# -*- coding: utf-8 -*-
from scrapy import Request

from proxy_spider.spiders import _BaseSpider
from utils.collections import shuffled_range


class XicidailiSpider(_BaseSpider):
    name = 'xicidaili'
    allowed_domains = ['www.xicidaili.com']

    def start_requests(self):
        for _type in ('nn', 'nt'):

            for _page in range(1, 100):
                if self.complete_condition():
                    break
                url = 'http://www.xicidaili.com/%s/%s' % (_type, _page)
                yield Request(url, dont_filter=True)

    def parse(self, response):
        for tr in response.xpath('//table[@id="ip_list"]//tr[@class]'):
            ex = tr.xpath('./td/text()').extract()
            ip = ex[0]
            port = ex[1]
            scheme = ex[5].lower()

            if ip and port and scheme in ('http', 'https'):
                yield self.build_check_recipient(ip, port, scheme)
