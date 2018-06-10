# coding: utf-8
from scrapy import cmdline
import json

cmdline.execute("scrapy crawl checker".split())


# target = '/home/k/Documents/proxy_list.json'
#
# with open('./proxy_list.json') as f:
#     new = json.load(f)
#
# with open(target, 'w') as f:
#     old = json.load(f)
#     for p in new:
#         if p not in old:
#             old.append(p)
#     json.dump(target, old)

