# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import time

from scrapy import log
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.httpobj import urlparse_cached
from scrapy.utils.response import get_meta_refresh
from six.moves.urllib.request import proxy_bypass

from service.proxy.proxy import blocking_proxy_srv


class CustomRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        url = response.url

        if response.status in [301, 307]:
            log.msg("trying to redirect us: %s" % url, level=log.INFO)
            reason = 'redirect %d' % response.status

            return self._retry(request, reason, spider) or response
        interval, redirect_url = get_meta_refresh(response)
        # handle meta redirect

        if redirect_url:
            log.msg("trying to redirect us: %s" % url, level=log.INFO)
            reason = 'meta'

            return self._retry(request, reason, spider) or response

        hxs = HtmlXPathSelector(response)
        # test for captcha page
        captcha = hxs.select(
            ".//input[contains(@id, 'captchacharacters')]").extract()

        if captcha:
            log.msg("captcha page %s" % url, level=log.INFO)
            reason = 'capcha'

            return self._retry(request, reason, spider) or response

        return response


class PureRedisMiddleware(HttpProxyMiddleware):
    """
    Straightly fetch proxy from redis database.
    Waiting to be reconstructed.
    """

    def __init__(self,
                 crawler,
                 auth_encoding):

        self.anonymity = 'anonymous'

        self.crawler = crawler
        self.logger = crawler.spider.logger
        self.auth_encoding = auth_encoding
        self.srv = blocking_proxy_srv
        self.settings = crawler.settings
        self.use_proxy_rate = self.settings.get('USE_PROXY_TO_CRAWL', 1)
        # print(self.raw_rate)

    def fetch_proxy(self, scheme):
        """
        Get proxy from fpserver by given scheme.

        :scheme: `str` proxy protocol
        :return:
            url, scheme
        """
        result = None

        params = {
            "scheme": scheme,
            # "anonymity": self.anonymity,
            "count": 1,
        }
        try:
            keys = self.srv.query(params, return_keys=True)
        except:
            self.logger.exception("Failed to fetch proxy")
        else:
            if keys:
                url = self.srv.cli.hget(keys[0], 'url')
                result = self._get_proxy(url, scheme)

        return result

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING',
                                             'latin-l')

        return cls(crawler, auth_encoding)

    def _set_proxy(self, request, scheme):
        _fetched = self.fetch_proxy(scheme)

        if not _fetched:
            return

        creds, proxy = _fetched
        request.meta['proxy'] = proxy
        self.logger.debug('Applied proxy: %s' % proxy)

        if creds:
            request.headers['Proxy-Authorization'] = b'Basic' + creds

    def process_request(self, request, spider):
        # ignore if proxy is already set

        if 'proxy' in request.meta:
            if request.meta['proxy'] is None:
                return
            # extract credentials if present
            creds, proxy_url = self._get_proxy(request.meta['proxy'], '')
            request.meta['proxy'] = proxy_url

            if creds and not request.headers.get('Proxy-Authorization'):
                request.headers['Proxy-Authorization'] = b'Basic ' + creds

            return

        parsed = urlparse_cached(request)
        scheme = parsed.scheme

        if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
            return

        if self.use_proxy_rate < 1:
            if random.random() < self.use_proxy_rate:
                self._set_proxy(request, scheme)
        else:
            self._set_proxy(request, scheme)


class RandomUserAgentMiddleware:
    """This middleware allows spiders to override the user_agent"""

    def __init__(self):
        self.user_agents = None

    def spider_opened(self, spider):
        from proxy_spider.const import user_agents
        self.user_agents = user_agents

    def process_request(self, request, spider):
        if self.user_agents:
            ua = random.choice(self.user_agents)
            request.headers.setdefault(b'User-Agent', ua)


class TimerMiddleware:

    def process_request(self, request, spider):
        request.meta['_start_time'] = time.time()
