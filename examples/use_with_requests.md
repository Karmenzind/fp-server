
This page shows how to use fp-server with `requests` in your python code.


```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from urllib.parse import urljoin, urlparse


FP_SERVER_ADDR = 'http://localhost:12345'
FP_SERVER_API = urljoin(FP_SERVER_ADDR, '/api/proxy/')


def fetch_proxy(url, anonymity='anonymous'):
    """
    Get proxy from fpserver by given url.

    :url:           the url you want to request
    :anonymity:     `transparent` or `anonymous`
    :return:        {scheme: url}
    """
    _parse = urlparse(url)
    scheme = _parse[0]

    params = {
        "scheme": scheme,
        "anonymity": anonymity,
    }
    text = None
    try:
        req = requests.get(FP_SERVER_API, params=params)
        text = req.text
        data = req.json()
    except:
        print("Failed to fetch proxy: %s" % text)
    else:
        _code = data.get('code')
        _proxies = data.get('data', {}).get('detail', [])

        if (_code is not 0) or (not _proxies):
            print(
                'Response of fetch_proxy: %s' % data)
            return

        proxy_info = _proxies[0]
        proxy_url = proxy_info['url']
        result = {scheme: proxy_url}
        print("Got proxy: ", result)
        return result


# say, the site is 'baidu'
url = 'https://baidu.com'
# get scheme and proxy
_p = fetch_proxy(url)
# build a request
r = requests.get(url,
                 proxies=_p,
                 timeout=20,
                 # and other parameters
                 )
print(r.status_code)
print(r.text)

```
