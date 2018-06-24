# fp-server

免费代理服务器，基于[Tornado](http://www.tornadoweb.org/en/stable/#)和[Scrapy](https://scrapy.org/)，在本地搭建属于自己的代理池

特性：
- 持续爬取新的免费代理，检测可用后存入本地数据库
- 完全异步，支持高并发
- 易用的HTTP API
- 周期性检测代理可用性，自动更新

> 走过路过给个star……  \_(:ι」∠)\_

已经测试通过的环境：
- Archlinux; Python-3.6.5
- Debian(WSL, Raspbian); Python-3.5.3

**代码暂不支持直接在Windows上运行，Windows用户请[选择Docker方式部署](#使用docker)或使用WSL……**

## 目录 ##

<!-- vim-markdown-toc GFM -->

* [安装使用](#安装使用)
    * [使用Docker](#使用docker)
    * [手动安装部署 ###](#手动安装部署-)
* [Web接口](#web接口)
    * [获取代理](#获取代理)
    * [查看状态](#查看状态)
* [配置](#配置)
    * [介绍](#介绍)
    * [修改](#修改)
* [代理来源](#代理来源)
* [FAQ](#faq)
* [问题和需求](#问题和需求)

<!-- vim-markdown-toc -->

## 安装使用 ##

首先安装[Redis数据库](https://redis.io/)，然后选取下列方式之一安装部署本项目。
安装完成之后，通过[API](#web接口)获取代理

### 使用Docker ###

**最简单**的安装部署方式是使用[Docker](https://www.docker.com/)，安装Docker后执行如下命令：
```bash
# 下载镜像
docker pull karmenzind/fp-server:stable
# 启动容器
docker run -itd --name fpserver --net="host" karmenzind/fp-server:stable
# 检查容器内部输出
docker logs -f fpserver
```
更改配置请查看[下文](#配置)

### 手动安装部署 ### 

1. 安装`python>=3.5`(我用的是Python-3.6.5)
2. 克隆这个项目 
3. 安装所需的Python包
```bash
pip install -r requirements.txt
```
4. 阅读[配置介绍](#配置)，根据需要修改
5. 启动服务
```bash
python ./src/main.py
```

## Web接口 ##

一般返回格式
```json
{
    "code": 0,
    "msg": "ok",
    "data": {}
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
            }
            ]
        }
    }
    ```

**截图**

![](https://raw.githubusercontent.com/Karmenzind/i/master/fp-server/proxy_get.png)

### 查看状态 ###

查看服务状态。包含：
-   正在运行的爬虫
-   Stored proxies

```
GET /api/status/
```

没有参数

**screenshot**

![](https://raw.githubusercontent.com/Karmenzind/i/master/fp-server/status.png)

## 配置 ##

### 介绍

配置文件采用YAML格式，定义和默认值如下：

```yaml
# 服务运行端口
HTTP_PORT: 12345

# 在终端打印输出，不写入文件
CONSOLE_OUTPUT: 1

# 日志设置
# dir和filename生效需要先设置CONSOLE_OUTPUT为0
LOG: 
  level: 'debug'
  dir: './logs'
  filename: 'fp-server.log'

REDIS:
  host: '127.0.0.1'
  port: 6379
  db: 0
  password:

# 本地要存储的代理总数
# 超过这个数目后，服务会停止爬取新的代理
# 根据你的需要来合理设置
PROXY_STORE_NUM: 500

# 设定周期，定时检查每个代理可用性
# 每个代理都会存储自己的最后检查时间，动态检查
PROXY_STORE_CHECK_SEC: 3600
```

### 修改

- 使用Docker部署:
    - 在本地新建目录，如`/x/config_dir`，在其中新建配置文件`config.yml`，然后将docker-run命令修改如下：
        ```
        docker run -itd --name fpserver --net="host" -v "/x/config_dir":"/fps-config" karmenzind/fp-server:stable
        ```
    - 外部`config.yml`的内容可以为上述配置项的子集，例如：
        ```
        PROXY_STORE_NUM: 100
        LOG:
            level: 'info'
        PROXY_STORE_CHECK_SEC: 7200
        ```
        其他配置项会自动采用内部配置
    - 如果要指定日志文件，**不要**修改`config.yml`中的`LOG-dir`。在本地新建日志目录，如`/x/log_dir`，结合上一步，修改docker-run命令为：
        ```
        docker run -itd --name fpserver --net="host" -v "/x/config_dir":"/fps_config" -v "/x/log_dir":"/fp_server/logs" karmenzind/fp-server:stable
        ```
- 手动方式部署：
    - 直接修改项目内文件: `src/config/config.yml`

## 代理来源 ##

这个列表还在增加，欢迎贡献新的代理网站给我，我会将它加进项目里

目前支持:
- [x] [西刺代理](http://www.xicidaili.com)
- [x] [快代理](http://www.kuaidaili.com)
- [x] [云代理](http://www.ip3366.net)
- [x] [66免费代理](http://www.66ip.cn/)
- [x] [无忧代理](http://www.data5u.com/free/index.shtml)
- [x] [3464](http://www.3464.com/data/Proxy/http/)
- [x] [coderbusy](https://proxy.coderbusy.com/)
- [x] [ip181](http://www.ip181.com/)
- [x] [iphai](http://www.iphai.com/free/ng)
- [ ] [万能代理](http://wndaili.cn)
- [ ] [小幻代理](https://ip.ihuan.me) (figuring)
- [ ] [89免费代理](http://www.89ip.cn/)(figuring)
- [ ] <del>[baizhongsou](http://ip.baizhongsou.com/)</del> (stop providing free proxies)

感谢: [Golmic](https://github.com/lujqme) [Eric_Chan](https://github.com/CL545740896/)

## FAQ ##

-   代理可用性如何？

    fp-server在爬取代理时会先检测可用性（包括速度和匿名性），检测完毕后才会入库，不可用的直接抛弃，所以你获取到的都是相对可用的代理。

-   存储代理数目`PROXY_STORE_NUM`设置多少合适？有上限么？

    根据你自己的需求来合理设置。假如只是一个普通的爬虫项目，那么设置为300到500就可以了，因为fp-server会持续自检更新代理，数目过大没有意义。数目设置暂时没有上限，我在攒够一万个活动（可用的）代理后停止了测试，因为目前代理来源有限。根据项目关注度，我会持续增加代理来源。

-   怎么把它用到我的项目里？

    我写了一个[可以直接用在Scrapy项目里的middleware](./examples/middleware_for_scrapy.md)。后面有空我会写更多示例代码。


## 问题和需求 ##

欢迎大家反馈，这样我才有动力维护

如果有Bug或者建议，请直接[创建issue](https://github.com/Karmenzind/fp-server/issues/new) 
