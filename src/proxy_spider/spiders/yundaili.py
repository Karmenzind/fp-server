# -*- coding: utf-8 -*-

from scrapy import Request

from proxy_spider.spiders import _BaseSpider


class YundailiSpider(_BaseSpider):
    name = 'yundaili'
    allowed_domains = ['www.ip3366.net']

    def start_requests(self):
        url = 'http://www.ip3366.net/free/?page=1'
        # url = 'http://example.com'
        meta = {
            'max_retry_times': 10,
            # 'download_timeout': 10,
        }
        yield Request(url, dont_filter=True, meta=meta)

    def parse(self, response):
        for p in response.xpath('//table/tbody/tr'):
            ex = p.xpath('./td/text()').extract()
            ip = ex[0]
            port = ex[1]
            scheme = ex[3].lower()

            if ip and port and scheme in ('http', 'https'):
                yield self.build_check_recipient(ip, port, scheme)
