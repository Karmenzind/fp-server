# -*- coding: utf-8 -*-

from proxy_spider.spiders import _BaseSpider


class A3464Spider(_BaseSpider):
    name = '3464'
    allowed_domains = ['3464.com']
    start_urls = ['http://www.3464.com/data/Proxy/http/']

    custom_settings = {
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 20
    }

    def parse(self, response):
        info = response.xpath(
            '//div[@class="CommonBody"]/table[6]/tr[4]/td/table/tr'
        )

        for x in info[1:]:
            data = x.xpath('td/text()').extract()

            if data:
                ip = data[0]
                port = data[1]
                scheme = 'http'
                yield self.build_check_recipient(ip, port, scheme)
