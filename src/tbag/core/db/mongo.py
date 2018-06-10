# -*- coding:utf-8 -*-

"""
mongodb async操作接口

Date:   2017/05/08
Update:
        2017/07/24  1、增加 find_one_and_update 接口;
                    2、增加 find_one_and_delete 接口;
        2017/08/16  1、增加数据库连接鉴权;
        2017/12/12  1、初始化参数去除port;
                    2、修改基类名DBBase为MongoDBBase;
        2017/12/29  1、修复bug: 处理查询条件里_id的各种类型;
"""

import copy

import motor
from bson.objectid import ObjectId
from urllib.parse import quote_plus

from tbag.utils import tools
from tbag.utils import log as logger


MONGO_CONN = None
DELETE_FLAG = 'delete'  # True 已经删除，False 或者没有该字段表示没有删除


def initMongodb(host='127.0.0.1:27017', username='', password='', dbname='admin'):
    """ 初始化mongodb连接
    """
    if username and password:
        uri = 'mongodb://{username}:{password}@{host}/{dbname}'.format(username=quote_plus(username),
                                                                       password=quote_plus(password),
                                                                       host=quote_plus(host),
                                                                       dbname=dbname)
    else:
        uri = "mongodb://{host}/{dbname}".format(host=host, dbname=dbname)
    mongo_client = motor.motor_tornado.MotorClient(uri)
    global MONGO_CONN
    MONGO_CONN = mongo_client
    logger.info('create mongodb connection pool.')


class MongoDBBase(object):
    """ mongodb 数据库操作接口
    """

    def __init__(self):
        """ 初始化
        * self._db 初始化连接的数据库，子类指定
        * self._table 初始化连接的colletion，子类指定
        """
        self.conn = MONGO_CONN
        self.dao = self.conn[self._db][self._table]

    async def get_list(self, spec={}, fields=None, sort=[], skip=0, limit=9999):
        """ 批量获取数据
        @param spec 查询条件
        @param fields 返回数据的字段
        @param sort 排序规则
        @param skip 查询游标
        @param limit 返回数据条数
        * NOTE: 必须传入limit，否则默认返回数据条数可能因为pymongo的默认值而改变
        """
        if '_id' in spec:
            spec['_id'] = self._convert_id_object(spec['_id'])
        spec[DELETE_FLAG] = {'$ne': True}
        datas = []
        cursor = self.dao.find(spec, fields, sort=sort, skip=skip, limit=limit)
        async for item in cursor:
            item['_id'] = str(item['_id'])
            datas.append(item)
        return datas

    async def find_one(self, spec={}, fields=None, sort=[]):
        """ 查找单条数据
        @param spec 查询条件
        @param fields 返回数据的字段
        @param sort 排序规则
        """
        data = await self.get_list(spec, fields, sort, limit=1)
        if data:
            return data[0]
        else:
            return None

    async def count(self, spec={}):
        """ 计算数据条数
        @param spec 查询条件
        @param n 返回查询的条数
        """
        spec[DELETE_FLAG] = {'$ne': True}
        n = await self.dao.count(spec)
        return n

    async def insert(self, docs_data):
        """ 插入数据
        @param docs_data 插入数据 dict或list
        @param ret_ids 插入数据的id列表
        """
        docs = copy.deepcopy(docs_data)
        ret_ids = []
        is_one = False
        create_time = tools.get_utc_time()
        if not isinstance(docs, list):
            docs = [docs]
            is_one = True
        for doc in docs:
            doc['_id'] = ObjectId()
            doc['create_time'] = create_time
            doc['modify_time'] = create_time
            ret_ids.append(str(doc['_id']))
        self.dao.insert_many(docs)
        if is_one:
            return ret_ids[0]
        else:
            return ret_ids

    async def update(self, spec, update_fields, upsert=False, multi=False):
        """ 更新
        @param spec 更新条件
        @param update_fields 更新字段
        @param upsert 如果不满足条件，是否插入新数据
        @param multi 是否批量更新
        @return modified_count 更新数据条数
        """
        spec[DELETE_FLAG] = {'$ne': True}
        if '_id' in spec:
            spec['_id'] = self._convert_id_object(spec['_id'])
        set_fields = update_fields.get('$set', {})
        set_fields['modify_time'] = tools.get_utc_time()
        update_fields['$set'] = set_fields
        if not multi:
            result = await self.dao.update_one(spec, update_fields, upsert=upsert)
            return result.modified_count
        else:
            result = await self.dao.update_many(spec, update_fields, upsert=upsert)
            return result.modified_count

    async def delete(self, spec):
        """ 软删除
        @param spec 删除条件
        @return delete_count 删除数据的条数
        """
        spec[DELETE_FLAG] = {'$ne': True}
        if '_id' in spec:
            spec['_id'] = self._convert_id_object(spec['_id'])
        update_fields = {'$set': {DELETE_FLAG: True}}
        delete_count = await self.update(spec, update_fields, multi=True)
        return delete_count

    async def remove(self, spec, multi=False):
        """ 彻底删除数据
        @param spec 删除条件
        @param multi 是否全部删除
        @return deleted_count 删除数据的条数
        """
        if not multi:
            result = await self.dao.delete_one(spec)
            return result.deleted_count
        else:
            result = await self.dao.delete_many(spec)
            return result.deleted_count

    async def distinct(self, key, spec={}):
        """ distinct查询
        @param key 查询的key
        @param spec 查询条件
        @return result 过滤结果list
        """
        spec[DELETE_FLAG] = {'$ne': True}
        if '_id' in spec:
            spec['_id'] = self._convert_id_object(spec['_id'])
        result = await self.dao.distinct(key, spec)
        return result

    async def find_one_and_update(self, spec, update_fields, upsert=False, return_document=False, fields=None):
        """ 查询一条指定数据，并修改这条数据
        @param spec 查询条件
        @param update_fields 更新字段
        @param upsert 如果不满足条件，是否插入新数据，默认False
        @param return_document 返回修改之前数据或修改之后数据，默认False为修改之前数据
        @param fields 需要返回的字段，默认None为返回全部数据
        @return result 修改之前或之后的数据
        """
        spec[DELETE_FLAG] = {'$ne': True}
        if '_id' in spec:
            spec['_id'] = self._convert_id_object(spec['_id'])
        set_fields = update_fields.get('$set', {})
        set_fields['modify_time'] = tools.get_utc_time()
        update_fields['$set'] = set_fields
        result = await self.dao.find_one_and_update(spec, update_fields, projection=fields, upsert=upsert,
                                                    return_document=return_document)
        if result and '_id' in result:
            result['_id'] = str(result['_id'])
        return result

    async def find_one_and_delete(self, spec={}, fields=None):
        """ 查询一条指定数据，并删除这条数据
        @param spec 删除条件
        @param fields 需要返回的字段，默认None为返回全部数据
        @param result 删除之前的数据
        """
        spec[DELETE_FLAG] = {'$ne': True}
        if '_id' in spec:
            spec['_id'] = self._convert_id_object(spec['_id'])
        result = await self.dao.find_one_and_delete(spec, projection=fields)
        if result and '_id' in result:
            result['_id'] = str(result['_id'])
        return result

    def _convert_id_object(self, origin):
        """ 将字符串的_id转换成ObjectId类型
        """
        if isinstance(origin, str):
            return ObjectId(origin)
        elif isinstance(origin, (list, set)):
            return [ObjectId(item) for item in origin]
        elif isinstance(origin, dict):
            for key, value in origin.items():
                origin[key] = self._convert_id_object(value)
        return origin


__all__ = [initMongodb, MongoDBBase]
