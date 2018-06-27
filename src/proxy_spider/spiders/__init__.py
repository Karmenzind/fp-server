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

import requests
import config
from proxy_spider import utils
from proxy_spider.items import Proxy
from service.proxy.functions import build_key, valid_format
from service.proxy.proxy import blocking_proxy_srv

LOCAL_IP = None
IP_CHECKER_API = 'http://api.ipify.org/?format=json'


def get_local_ip():
    global LOCAL_IP
    if LOCAL_IP:
        return LOCAL_IP
    else:
        r = requests.get(IP_CHECKER_API)
        j = json.loads(r.text)
        LOCAL_IP = j['ip']
        return LOCAL_IP


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
            # ('http://ip-check.info/?lang=en/', self.parse_ipcheck),
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
            self.logger.debug('Got wrong format (%s, %s). Clear it.' % (ip, port))

            return {}

        if self.already_exists(spec):
            self.logger.debug('Got duplicated %s. Clear it.' % spec.values())

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

        self.logger.debug('Got unchecked %s' % item)

        return self.build_check_request(item)

    def build_check_request(self, item: Proxy):
        scheme = item.get('scheme')
        proxy_url = item.get('url')
        self.logger.debug('Checking %s' % proxy_url)

        url, response_parser = self.get_check_approach(scheme)
        url = url.format(scheme=scheme)

        timeout = getattr(config, 'CHECK_TIMEOUT', 20)
        meta = {
            'proxy': proxy_url,
            'max_retry_times': 5,
            'download_timeout': timeout,
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
            self.logger.exception(
                'While checking %s with %s, '
                'Failed to parse response %s. '
                % (item,
                   response.url,
                   response.text)
            )

        if got_ip.strip() == get_local_ip():
            item['anonymity'] = 'transparent'
        else:
            item['anonymity'] = 'anonymous'
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
