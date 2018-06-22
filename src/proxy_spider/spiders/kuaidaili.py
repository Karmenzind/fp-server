# -*- coding: utf-8 -*-

from scrapy import Request

from proxy_spider.spiders import _BaseSpider
from utils.collections import shuffled_range


class KuaidailiSpider(_BaseSpider):
    name = 'kuaidaili'
    allowed_domains = ['www.kuaidaili.com']

    def start_requests(self):
        meta = {
            # 'max_retry_times': 10,
            # 'download_timeout': 20,
        }
        pages = range(1, 100)

        for _type in ('inha', 'intr'):
            for _page in pages:
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
