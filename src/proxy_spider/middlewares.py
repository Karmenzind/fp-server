# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random

import requests
from scrapy import log
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.exceptions import NotConfigured
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


class FPServerMiddleware(HttpProxyMiddleware):
    """
    * This middleware is trying to figure out
      how to use this server in a general scrapy project

    A middleware, based on FPServer, continuesly providing random proxy.
    FPServer required.

    required config items: (Must/Optional)
        FP_SERVER_URL               M
        HTTPPROXY_AUTH_ENCODING     O   default: latin-l
        FP_SERVER_PROXY_ANONYMITY   O   default: random
            choices:    `transparent` `anonymous`
    """

    def __init__(self,
                 crawler,
                 auth_encoding,
                 fps_url,
                 anonymity,
                 fps_scheme):

        if not fps_url:
            raise NotConfigured

        self.anonymity = anonymity

        self.logger = crawler.logger
        self.crawler = crawler
        self.auth_encoding = auth_encoding

        """

        format:
            proxy: scheme://ip:port

            result = self._get_proxy(proxy, scheme)
        """

    def fetch_proxy(self, scheme):
        """
        Get proxy from fpserver by given scheme.

        :scheme: `str` proxy protocol
        :return:
            url, scheme
        """

        params = {
            "protocol": scheme,
            "anonymity": self.anonymity,
        }
        try:
            req = requests.get(self.fps_url, params=params)
            data = req.json()
        except:
            self.crawler.logger.exception("Failed to fetch proxy: %s"
                                          % req.text)
        else:
            _code = data.get('code')
            _msg = data.get('msg')
            _proxies = data.get('data', {}).get('items', [])

            if (_code is not 0) or (not _proxies):
                self.logger.warning('Response of fetch_proxy: %s'
                                    % data)

                return
            proxy_info = _proxies[0]
            proxy_url = proxy_info['url']

            return self._get_proxy(proxy_url, scheme)

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING',
                                             'latin-l')
        fps_url = crawler.settings.get('FP_SERVER_URL')
        fps_scheme = crawler.settings.get('FP_SERVER_PROXY_SCHEME')
        anonymity = crawler.settings.get('FP_SERVER_PROXY_ANONYMITY')

        return cls(crawler, auth_encoding, fps_url, anonymity, fps_scheme)

    def _set_proxy(self, request):
        _fetched = self.fetch_proxy(scheme)

        if not _fetched:
            return

        creds, proxy = _fetched
        request.meta['proxy'] = proxy

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

        # 'no_proxy' is only supported by http schemes

        if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
            return

        self._set_proxy(request, scheme)


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
            "anonymity": self.anonymity,
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
