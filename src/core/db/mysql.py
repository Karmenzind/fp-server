# -*- coding:utf-8 -*-

"""
MySQL async操作接口

Date:   2017/05/08
Update: 2017/12/17  1. 修改配置参数user为username;
"""

from tornado_mysql import pools, cursors
from utils import log as logger

pools.DEBUG = True
CONN_POOL = None


def initMySQL(host='127.0.0.1', port=3306, username='', password='', db='mysql'):
    """ 初始化mysql连接池
    @param host MySQL数据库ip
    @param port MySQL数据库端口
    @param username MySQL数据库用户名
    @param password MySQL数据库密码
    @param db 需要连接的数据库名
    """
    mysql_config = {
        'host': host,
        'port': port,
        'user': username,
        'passwd': password,
        'db': db,
        'cursorclass': cursors.DictCursor,
        'charset': 'utf8'
    }
    logger.info('mysql_config:', mysql_config)
    global CONN_POOL
    CONN_POOL = pools.Pool(mysql_config,
                           max_idle_connections=1,
                           max_recycle_sec=3)
    logger.info('create mysql connection pool.')


async def exec_cmd(sql):
    """ 执行mysql命令
    @param sql sql命令
    @result result 返回的执行结果
    """
    sql = sql.replace('\t', ' ').replace('\n', ' ')
    logger.debug('sql:', sql)
    cursor = await CONN_POOL.execute(sql)
    result = cursor.fetchall()
    return result


__all__ = [initMySQL, exec_cmd]
