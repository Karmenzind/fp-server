## Intro

This is a middleware for using fp-server in general scrapy project.
It will continuously fetch random proxy and set it **at each request**.

To use this in your project, you should:
1. keep the fp-server running
2. add the middleware code down below to your `middlewares.py`
2. modify your settings:
```python
# don't use scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware
# at the same time
DOWNLOADER_MIDDLEWARES = {
    'NameOfYourProject.middlewares.FPServerMiddleware': 745,
}

# follow your real settings
# your fp-server's address
FP_SERVER_URL = 'http://localhost:12345'
# anonymity: `anonymous` or `transparent` (default: random)
FP_SERVER_PROXY_ANONYMITY = 'anonymous'
# override the proxy that is already set (except for explicit None)
# before this middleware
FP_SERVER_FORCE_OVERRIDE = 1
# coding for auth (default: latin-l)
# HTTPPROXY_AUTH_ENCODING = 'latin-l'
```

## Middleware

Here is the code.

```python
# coding: utf-8
from urllib.parse import urljoin

import requests
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.exceptions import NotConfigured
from scrapy.utils.httpobj import urlparse_cached
from six.moves.urllib.request import proxy_bypass


class FPServerMiddleware(HttpProxyMiddleware):
    """
    A middleware, based on FPServer, continuesly fetch random proxy
    and set it for each request.
    FPServer required.
    """

    def __init__(self,
                 crawler,
                 auth_encoding,
                 fps_url,
                 anonymity,
                 force_override):

        if not fps_url:
            raise NotConfigured('FP_SERVER_URL not configured')

        self.fps_api = urljoin(fps_url, '/api/proxy/')

        self.anonymity = anonymity

        self.logger = crawler.spider.logger
        self.crawler = crawler
        self.auth_encoding = auth_encoding
        self.force_override = force_override

    def fetch_proxy(self, scheme):
        """
        Get proxy from fpserver by given scheme.

        :scheme: `str` proxy protocol
        :return:
            url, scheme
        """

        params = {
            "scheme": scheme,
            "anonymity": self.anonymity,
        }
        text = None
        try:
            req = requests.get(self.fps_api, params=params)
            text = req.text
            data = req.json()
        except:
            self.logger.exception("Failed to fetch proxy: %s" % text)
        else:
            _code = data.get('code')
            _proxies = data.get('data', {}).get('detail', [])

            if (_code is not 0) or (not _proxies):
                self.logger.warning(
                    'Response of fetch_proxy: %s' % data)

                return
            proxy_info = _proxies[0]
            proxy_url = proxy_info['url']

            return self._get_proxy(proxy_url, scheme)

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING',
                                             'latin-l')
        fps_url = crawler.settings.get('FP_SERVER_URL')
        anonymity = crawler.settings.get('FP_SERVER_PROXY_ANONYMITY')
        force_override = crawler.settings.get('FP_SERVER_FORCE_OVERRIDE', 0)

        return cls(crawler, auth_encoding, fps_url, anonymity, force_override)

    def _set_proxy(self, request, scheme):
        _fetched = self.fetch_proxy(scheme)

        if not _fetched:
            self.logger.debug('No proxy fetched from fp-server.')
            raise AssertionError('Please check your fp-server.')

        creds, proxy = _fetched
        request.meta['proxy'] = proxy
        self.logger.debug('Applied proxy (%s) for %s' % (proxy, request.url))

        if creds:
            request.headers['Proxy-Authorization'] = b'Basic' + creds

    def process_request(self, request, spider):
        # ignore if proxy is already set
        # except force_override is true and previous proxy is None
        if 'proxy' in request.meta:
            # take higher priority than force_override
            previous_proxy = request.meta['proxy']
            if previous_proxy is None:
                return

            if self.force_override:
                self.logger.debug('Forcely overrode the old proxy (%s).'
                                  % previous_proxy)
            else:
                # extract credentials if present
                creds, proxy_url = self._get_proxy(previous_proxy, '')
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

```
