# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from proxy_spider.spiders import _BaseSpider


class CoderbusySpider(_BaseSpider):
    name = 'coderbusy'
    allowed_domains = ['coderbusy.com']
    start_urls = [
        'https://proxy.coderbusy.com/classical/https-ready.aspx',
        'https://proxy.coderbusy.com/classical/anonymous-type/anonymous.aspx',
        'https://proxy.coderbusy.com/classical/anonymous-type/highanonymous.aspx',
        'https://proxy.coderbusy.com/classical/anonymous-type/transparent.aspx',
    ]

    custom_settings = {
        "DOWNLOAD_TIMEOUT": 20,
    }

    rules = (
        Rule(LinkExtractor(allow=(r'classical.+aspx.*page=\d+$', )),
             callback='parse_items',
             follow=True),
    )

    def parse_items(self, response):
        for tr in response.xpath('//table[@class="table"]/tbody/tr'):
            td = tr.xpath('./td[@class="port-box"]')
            ip = td.xpath('@data-ip').get()
            port = td.xpath('@data-i').get()

            for scheme in ('http', 'https'):
                yield self.build_check_recipient(ip, port, scheme)
