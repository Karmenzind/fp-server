# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import json
import random
import time

from scrapy import Request, exceptions
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from twisted.internet.error import (DNSLookupError, TCPTimedOutError,
                                    TimeoutError)

import config
from proxy_spider import utils
from proxy_spider.items import Proxy
from service.proxy.proxy import blocking_proxy_srv
from utils.proxy import build_key, valid_format


class _BaseSpider(CrawlSpider):
    srv = blocking_proxy_srv

    def complete_condition(self):
        num = int(getattr(config, 'PROXY_STORE_NUM', 0))
        keys = self.srv.get_all_keys()

        return len(keys) >= num

    def already_exists(self, spec):
        result = False
        existed = self.srv.keys_by_dict(spec)

        if existed:
            result = True

        return result

    def get_check_approach(self, scheme):
        # default_timeout = 10
        _both = [
            ('{scheme}://httpbin.org/ip', self.parse_httpbin),
            ('{scheme}://ipduh.com/anonymity-check/', self.parse_ipduh),
            ('{scheme}://api.ipify.org/?format=json', self.parse_ipify),
        ]
        _http = [
            ('http://ip-check.info/?lang=en/', self.parse_ipcheck),
        ]
        _https = [
        ]

        if scheme == 'http':
            result = random.choice(_both + _http)
        else:
            result = random.choice(_both + _https)

        return result

    def build_check_recipient(self, ip, port, scheme,
                              user=None, password=None):
        """
        1. build a request for availability checking
        2. drop it if already existed

        :return: Request
        """

        if self.complete_condition():
            raise exceptions.CloseSpider('Enough items')

        spec = dict(ip=ip, port=port, scheme=scheme)

        if not valid_format(spec):
            self.logger.debug('Wrong format: (%s, %s)' % (ip, port))

            return {}

        if self.already_exists(spec):
            self.logger.debug('Dropped duplicated: %s' % spec.values())

            return {}  # drop it

        proxy_url = utils.build_proxy_url(ip, port, scheme, user, password)
        need_auth = bool(user and password)
        item = Proxy(
            ip=ip,
            scheme=scheme,
            port=port,
            need_auth=need_auth,
            url=proxy_url,
        )

        if need_auth:
            item['user'], item['password'] = user, password

        return self.build_check_request(item)

    def build_check_request(self, item):
        scheme = item.get('scheme')
        proxy_url = item.get('url')
        self.logger.debug('Checking proxy: %s' % proxy_url)

        url, response_parser = self.get_check_approach(scheme)
        url = url.format(scheme=scheme)

        meta = {
            'proxy': proxy_url,
            'max_retry_times': 5,
            'download_timeout': 20,
            '_item_obj': item,
            '_response_parser': response_parser,
        }

        req = Request(url,
                      callback=self.check_ip,
                      meta=meta,
                      dont_filter=True)

        if self.name == 'checker':
            req.errback = self.check_ip_failed

        return req

    def check_ip(self, response):
        """
        check ip's availability and anonymity
        """
        item = response.meta['_item_obj']
        cur_ts = time.time()
        item['last_check'] = int(cur_ts)
        item['speed'] = cur_ts - response.meta['_start_time']
        item['fail_times'] = 0

        parser = response.meta['_response_parser']
        got_ip = ''
        try:
            got_ip = parser(response) or ''
        except:
            self.logger.exception('Failed when parse response.')

        if item['ip'] == got_ip.strip():
            item['anonymity'] = 'anonymous'
        else:
            item['anonymity'] = 'transparent'
        yield item

    def check_ip_failed(self, failure):
        self.logger.error(repr(failure))
        item = failure.request.meta['_item_obj']
        key = build_key(item)
        self.srv.add_failure(key)

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def parse_httpbin(self, response):
        return json.loads(response.text)['origin']

    def parse_ipcheck(self, response):
        return response.xpath('//section[@id="content"]/h1[2]/span/a/text()').get()

    def parse_ipduh(self, response):
        return response.xpath(
            '//table[@id="hm"]/tr/td[contains(text(), "public IP address")]/following-sibling::td/text()').get()

    def parse_ipify(self, response):
        return json.loads(response.text)['ip']
