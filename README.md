# fp-server

Free proxy collector and provider based on [Tornado](http://www.tornadoweb.org/en/stable/#) and [Scrapy](https://scrapy.org/).

It crawled free proxies from Internet and provide them by HTTP API.
You can use it as a proxy pool in your crawler project.

## Contents ##

<!-- vim-markdown-toc GFM -->

* [Get started](#get-started)
* [web APIs](#web-apis)
    * [get proxies](#get-proxies)
* [Config](#config)
* [Source webs](#source-webs)
* [Bugs and feature requests](#bugs-and-feature-requests)
* [TODOs](#todos)

<!-- vim-markdown-toc -->

## Get started ##

-   The easy way to use fp-server is via docker. After installed docker, just run:
    ```bash
    docker pull
    docker run
    ```
    to install/update and start the server.
-   Or you can do it manually.
    1. Install base requirements: `python>=3.5`(I use Python-3.6.5) `redis`
    2. Clone this repo. 
    3. Install python packages by: 
    ```bash
    pip install -r requirements
    ```
    4. Read the [config](#config) and modify it according to your need.
    5. Start the server:
    ```bash
    python ./src/main.py
    ```
-   Then use the [APIs](#apis) to get proxies.

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
 protocol               | O                 | choices:`HTTP` `HTTPS`                                               | both*
anonymity               | O                 | choices:`transparent` `anonymous`                                    | both
(TODO)<br>sort_by_speed | O                 | choices:<br>1: desending order<br>0: no order<br>-1: ascending order | 0

- both: include all type, not grouped

**example**

-   To acquire 10 proxies in HTTP scheme with anonymity:
    ```
    GET /api/proxy/?num=10&protocol=HTTP&anonymity=anonymous
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
                "protocol": "HTTP",
                "url": "http://xxx.xxx.xxx.xx:xxxx",
                "anonymity": "transparent"
            },
            {
                "port": 2000,
                "ip": "xxx.xxx.xx.xxx",
                "protocol": "HTTP",
                "url": "http://xxx.xxx.xxx.xx:xxxx",
                "anonymity": "transparent"
            },
            ...
            ]
        }
    }
    ```



## Config ##

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

## TODOs ##

*   Divide log module
*   More api
*   Bring in Docker
*   Web frontend via bootstrap
*   Add user-agent pool

