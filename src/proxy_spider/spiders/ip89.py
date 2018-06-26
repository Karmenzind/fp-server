# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from proxy_spider.spiders import _BaseSpider


class Ip89Spider(_BaseSpider):
    name = 'ip89'
    allowed_domains = ['www.89ip.cn']

    rules = (
        Rule(LinkExtractor(allow=(r'index_\d+\.html$',)),
             callback='parse_items',
             follow=True),
    )

    def start_requests(self):
        base = 'http://www.89ip.cn'
        meta = {
            'max_retry_times': 10,
            # 'download_timeout': 20,
        }

        # pages = shuffled_range(1, 100)

        for _page in range(1, 100):
            if self.complete_condition():
                break
            url = urljoin(base, '/index_%s.html' % _page)
            yield Request(url,
                          callback=self.parse_items,
                          meta=meta,
                          dont_filter=True)

    def parse_items(self, response):
        for tr in response.xpath('//table[@class="layui-table"]/tbody/tr'):
            ex = tr.xpath('./td/text()').extract()
            ip = ex[0].strip()
            port = ex[1].strip()

            if ip and port:
                for scheme in ('http', 'https'):
                    yield self.build_check_recipient(ip, port, scheme)
