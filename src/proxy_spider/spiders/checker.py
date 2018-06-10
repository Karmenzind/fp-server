# coding: utf-8
from proxy_spider.spiders import _BaseSpider
from service.proxy.proxy import blocking_proxy_srv
from utils.spider import need_check


class CheckerSpider(_BaseSpider):
    """
    Check proxy's availability and anonymity.
    """
    name = 'checker'
    # allowed_domains = ['*']
    srv = blocking_proxy_srv

    def start_requests(self):
        keys = self.srv.get_all_keys()

        for key in keys:
            data = self.srv.hgetall_dict(key)
            last_check = data.get('last_check', 0)

            if need_check(last_check):
                yield self.build_check_request(data)
