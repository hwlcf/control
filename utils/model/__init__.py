#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description of this file
    
    :author: Zhidong :)
    :copyright: (c) 2018, Tungee
    :date created: 2018-03-20
    
"""
from pymongo import MongoClient

from configs import MongoConf


def get_db(db, host='localhost:27017', is_auth=False,
           user='', pwd='', is_replica=False, replica=''):
    """
    获取db实例
    :param db: 数据库
    :param host: 服务器地址
    :param is_auth: 是否验证用户
    :param user: 用户名
    :param pwd: 密码
    :param is_replica:  是否是集群
    :param replica: 集群名称
    :return db:
    """
    if is_replica:
        url = 'mongodb://%s/?replicaSet=%s' % (host, replica)
    else:
        url = host

    client = MongoClient(url, connect=False, maxPoolSize=10)
    db = client[db]

    if is_auth:
        db.authenticate(user, pwd)

    return db


_db = get_db(
    MongoConf.DB, MongoConf.HOST, MongoConf.IS_AUTH,
    MongoConf.USER, MongoConf.PWD,
    MongoConf.IS_REPLICA, MongoConf.REPLICA)
