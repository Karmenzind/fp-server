# fp-server

Free proxy server based on [Tornado](http://www.tornadoweb.org/en/stable/#) and [Scrapy](https://scrapy.org/).

Build your own proxy pool!

Features:
- continuesly crawling and providing free proxy
- with friendly and easy-to-use HTTP api
- asynchronous and high-perfermance
- support high con-concurrent
- automatically check proxy in cycle and ditch unavailable ones

> 中文文档正在写…… _(:ι」∠)_

## Contents ##

<!-- vim-markdown-toc GFM -->

* [Get started](#get-started)
* [web APIs](#web-apis)
    * [get proxies](#get-proxies)
    * [check status](#check-status)
* [Config](#config)
* [Source webs](#source-webs)
* [Bugs and feature requests](#bugs-and-feature-requests)
* [TODOs](#todos)

<!-- vim-markdown-toc -->

## Get started ##

1. Install base requirements: `python>=3.5`(I use Python-3.6.5) `redis`
2. Clone this repo. 
3. Install python packages by: 
```bash
pip install -r requirements.txt
```
4. Read the [config](#config) and modify it according to your need.
5. Start the server:
```bash
python ./src/main.py
```
6. Then use the [APIs](#apis) to get proxies.

## web APIs ##

typical response:
```json
{
    "code": 0,
    "msg": "ok",
    "data": {
        ...
    }
}
```

-   code: result of event (not http code), 0 for sucess
-   msg: message for failed event
-   data: detail for sucessful event

### get proxies ###

```
GET /api/proxy/
``` 

 params                 | Must/<br>Optional | detail                                                               | default
------------------------|-------------------|----------------------------------------------------------------------|---------|
 count                  | O                 | the number of proxies you need                                       | 1
 scheme                 | O                 | choices:`HTTP` `HTTPS`                                               | both*
anonymity               | O                 | choices:`transparent` `anonymous`                                    | both
(TODO)<br>sort_by_speed | O                 | choices:<br>1: desending order<br>0: no order<br>-1: ascending order | 0

- both: include all type, not grouped

**example**

-   To acquire 10 proxies in HTTP scheme with anonymity:
    ```
    GET /api/proxy/?num=10&scheme=HTTP&anonymity=anonymous
    ```
    The response:
    ```json
    {
        "code": 0,
        "msg": "ok",
        "data": {
            "count": 9,
            "items": [
            {
                "port": 2000,
                "ip": "xxx.xxx.xx.xxx",
                "scheme": "HTTP",
                "url": "http://xxx.xxx.xxx.xx:xxxx",
                "anonymity": "transparent"
            },
            ...
            ]
        }
    }
    ```

**screenshot**

![](./pics/proxy_get.png)

### check status ###

Check server status. Include:
-   Running spiders
-   Stored proxies

```
GET /api/status/
```

No params.

**screenshot**

![](./pics/status.png)

## Config ##

Path: `{repo}/src/config/common.py`

- `HTTP_PORT`   decide which http port to run on (default: 12345)
- `CONSOLE_OUTPUT`  if set to 1, the server will print log to console other than file (default: 1)
- `LOG`  log config, including:
    - `level` `dir` and `filename`, logging to file requires `CONSOLE_OUTPUT = 0`
- `REDIS`  redis database config, including:
    - `host` `port` `db`
- `PROXY_STORE_NUM` the number of proxy you need (default 500)
    - After reached this number, the crawler stopped crawling new proxies.
    - Set it depending on your need. 
- `PROXY_STORE_CHECK_SEC` every proxy will be checked in period
    - It's for each single proxy, not the checker spider.

## Source webs ##

Growing……

- [ x ] [西刺代理](www.xicidaili.com)
- [ x ] [快代理](http://www.kuaidaili.com)
- [ x ] [云代理](http://www.ip3366.net) (partial)
- [   ] [小幻代理](https://ip.ihuan.me) (figuring)
- [   ] [万能代理](http://wndaili.cn)
- [   ] [89免费代理](http://www.89ip.cn/)
- [   ] [66免费代理](http://www.66ip.cn/)

## Bugs and feature requests ##

I need your feedback to make it better.<br>
Please [create an issue](https://github.com/Karmenzind/fp-server/issues/new) for any problems or advice.

Known bugs:
*   Many wierd `None`... thought relavant to insecure thread
*   Block while using Tornado-4.5.3

## TODOs ##

*   Divide log module
*   More detailed api
*   Bring in Docker
*   Web frontend via bootstrap
*   Add user-agent pool

