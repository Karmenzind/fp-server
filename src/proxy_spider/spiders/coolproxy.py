# -*- coding: utf-8 -*-
import base64
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from proxy_spider.spiders import _BaseSpider
from utils.tools import str_rot13


class CoolproxySpider(_BaseSpider):
    name = 'coolproxy'
    allowed_domains = ['cool-proxy.net']
    start_urls = [
        'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:',
        'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:/page:2',
        'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:/page:3',
    ]

    rules = (
        Rule(
            link_extractor=LinkExtractor(
                allow=(r'proxies.*page:\d+.*',),
                restrict_xpaths=('//th[@class="pagination"]',),

            ),
            callback='parse_items',
            follow=True),
    )

    def parse_items(self, response):
        for tr in response.xpath('//table//tr')[1:]:
            ip_js = tr.xpath('./td/script/text()').get()

            if not ip_js:
                continue

            searched = re.search(r'str_rot13\("(.*)"', ip_js)

            if not searched:
                continue

            ip_encoded = searched.group(1)
            ip = base64.b64decode(str_rot13(ip_encoded)).decode('utf-8')

            if ip:
                ex = tr.xpath('./td/text()').extract()
                port = ex[0]

                for scheme in ('http', 'https'):
                    yield self.build_check_recipient(ip, port, scheme)
