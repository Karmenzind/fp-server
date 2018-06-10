# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field, Item


class Proxy(Item):
    ip = Field()
    port = Field()
    scheme = Field()  # HTTP or HTTPS
    anonymity = Field()

    url = Field()  # formed

    need_auth = Field()
    user = Field()
    password = Field()

    speed = Field()

    last_check = Field()
    fail_times = Field()
