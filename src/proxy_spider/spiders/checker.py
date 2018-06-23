# coding: utf-8
from proxy_spider.spiders import _BaseSpider
from service.proxy.functions import exceed_check_period, valid_format
from proxy_spider.items import Proxy


class CheckerSpider(_BaseSpider):
    """
    Check proxy's availability and anonymity.
    """
    name = 'checker'
    # allowed_domains = ['*']
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    }

    def start_requests(self):
        keys = self.srv.get_all_keys()

        for key in keys:
            data = self.srv.hgetall_dict(key)
            last_check = data.get('last_check', 0)

            if not valid_format(data):
                self.srv.delete(key, 'Error format %s' % data)

                continue

            if exceed_check_period(last_check):
                item = Proxy(**data)
                yield self.build_check_request(item)
