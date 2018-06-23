# coding: utf-8
from proxy_spider.spiders import _BaseSpider


class Data5uSpider(_BaseSpider):
    name = "data5u"
    allowed_domains = ["data5u.com"]
    # custom_settings = {
    #     # "DOWNLOAD_TIMEOUT": 20,
    # }

    start_urls = [
        "http://www.data5u.com/free/gngn/index.shtml",
        "http://www.data5u.com/free/gnpt/index.shtml",
        "http://www.data5u.com/free/gwgn/index.shtml",
        "http://www.data5u.com/free/gwpt/index.shtml",
        "http://www.data5u.com/free/index.shtml",
    ]

    def parse(self, response):
        iplist = response.xpath('//ul[@class="l2"]')

        for x in iplist[1:-1]:
            ip = x.xpath('span[1]/li/text()').extract_first()
            port = x.xpath('span[2]/li/text()').extract_first()
            scheme = str(
                x.xpath('span[4]/li/a/text()').extract_first()).upper()
            # type = x.xpath('span[3]/li/a/text()').extract_first()
            # print(ip, port, scheme, type)
            yield self.build_check_recipient(ip, port, scheme)
