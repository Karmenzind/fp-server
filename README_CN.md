# fp-server

免费代理服务器，基于[Tornado](http://www.tornadoweb.org/en/stable/#)和[Scrapy](https://scrapy.org/)，在本地搭建属于自己的代理池

目前特性：
- 持续爬取新的免费代理
- 易用的HTTP api
- 异步，支持高并发
- 周期性检测代理可用性，自动更新

> 走过路过给个star……  \_(:ι」∠)\_

已经测试通过的环境：
- Archlinux; Python-3.6.5
- Debian(wsl); Python-3.5.3

**Windows暂不支持……**

## 目录 ##

<!-- vim-markdown-toc GFM -->

* [安装使用](#安装使用)
* [Web接口](#web接口)
    * [获取代理](#获取代理)
    * [查看状态](#查看状态)
* [配置](#配置)
* [代理来源](#代理来源)
* [问题和需求](#问题和需求)
* [TODOs](#todos)

<!-- vim-markdown-toc -->

## 安装使用 ##

1. 安装基础软件 `python>=3.5`(我用的是Python-3.6.5) `redis`
2. 克隆这个项目 
3. 安装所需的Python包
```bash
pip install -r requirements.txt
```
4. 阅读[配置介绍](#config)，根据需要修改
5. 启动服务
```bash
python ./src/main.py
```
6. 通过[API](#web接口)获取代理

## Web接口 ##

一般返回格式
```json
{
    "code": 0,
    "msg": "ok",
    "data": {
        ...
    }
}
```

-   code: 事件状态(并非HTTP状态码), 0代表成功
-   msg: 事件相关信息
-   data: 返回数据

### 获取代理 ###

```
GET /api/proxy/
``` 

 参数                   | 必须(M)/<br>非必须(O) | 详情                                               | 默认
------------------------|-----------------------|----------------------------------------------------|-------|
 count                  | O                     | 获取的数目
 scheme                 | O                     | 协议。可选:`HTTP` `HTTPS`                          | both*
anonymity               | O                     | 匿名效果。可选:`transparent`透明， `anonymous`匿名 | both
(TODO)<br>sort_by_speed | O                     | 排序:<br>1: 降序<br>0: 乱序<br>-1: 升序            | 0

- both: 包括所有类型，不分组

**举例**

-   获取10个HTTP匿名代理:
    ```
    GET /api/proxy/?num=10&scheme=HTTP&anonymity=anonymous
    ```
    返回：
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

**截图**

![](./pics/proxy_get.png)

### 查看状态 ###

查看服务状态。包含：
-   正在运行的爬虫
-   Stored proxies

```
GET /api/status/
```

没有参数

**screenshot**

![](./pics/status.png)

## 配置 ##

配置文件路径: `{repo}/src/config/common.py`

- `HTTP_PORT`   服务运行端口 (默认: 12345)
- `CONSOLE_OUTPUT`  设置为1，日志输出到终端，不写入文件 (默认: 1)
- `LOG`  日志设置:
    - `level` `dir` 和 `filename`, 写入文件生效前提为`CONSOLE_OUTPUT = 0`
- `REDIS`  Redis数据库配置
    - `host` `port` `db`
- `PROXY_STORE_NUM` 本地要存储的代理总数
    - 超过这个数目后，服务会停止爬取新的代理
    - 根据你的需要来合理设置
- `PROXY_STORE_CHECK_SEC` 设定周期，定时检查每个代理可用性
    - 每个代理都会存储自己的最后检查时间，动态检查

## 代理来源 ##

这个列表还在增加

目前支持:
- [x] [西刺代理](http://www.xicidaili.com)
- [x] [快代理](http://www.kuaidaili.com)
- [x] [云代理](http://www.ip3366.net) (partial)
- [ ] [小幻代理](https://ip.ihuan.me) (figuring)
- [ ] [万能代理](http://wndaili.cn)
- [ ] [89免费代理](http://www.89ip.cn/)
- [ ] [66免费代理](http://www.66ip.cn/)

## 问题和需求 ##

欢迎大家反馈，这样我才有动力维护

如果有Bug或者建议，请直接[创建issue](https://github.com/Karmenzind/fp-server/issues/new) 

known bugs
*   Many wierd `None`... thought relavant to insecure thread
*   Block while using Tornado-4.5.3

## TODOs ##

*   Divide log module
*   More detailed api
*   Bring in Docker
*   Web frontend via bootstrap
*   Add user-agent pool

