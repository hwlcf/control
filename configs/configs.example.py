#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    configs.example.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Please copy content in this file to configs/__init__.py


"""
ROOT_PATH = ''
ALLOW_HOST_DOMAINS = []
API_WHITE_LIST = []  # 不受referrer限制的接口
HOST_ID = ''
CLUSTER_MEMBERS = []


class AppConf(object):
    """Config of flask application"""
    SECRET_KEY = ''
    SESSION_COOKIE_NAME = ''
    SESSION_COOKIE_DOMAIN = None
    DEBUG = False  # Change to True if in dev environment
    PORT = 10004
    BIND_IP = '0.0.0.0'
    ALLOW_HOST_DOMAINS = []
    API_WHITE_LIST = []
    LOGIN_API_LIMITER_STR = '500/hour;60/minute'

    # Domain
    HOST_DOMAIN = 'mockingbird-dev.tangees.com'
    OSS_DOMAIN = ''

    # Blueprint switch
    OPEN_PRODUCT_API = True

    # api salt
    CUR_APP_API_SALT = ''  # 当前APP API salt


class RedisConf(object):
    """Config of Redis"""
    HOST = 'localhost'
    PORT = 6379
    DB = 0
    PASSWORD = ''
    URL = 'redis://localhost:6379/0'


class MongoConf(object):
    """Config of mongo"""
    HOST = 'localhost:27017'
    DB = 'test'
    IS_AUTH = False
    USER = ''
    PWD = ''
    IS_REPLICA = False
    REPLICA = ''


class EsConf(object):
    """Config of elasticsearch"""
    HOSTS = 'localhost:9200'


class CeleryConf(object):
    """Config of celery"""
    DEFAULT_BROKER_URL = ''
    # default_celery并发
    DEFAULT_CELERY_CONCURRENCE = 1


class ProjectConf(object):
    """Config of project"""
    PROJECT_NAME = 'default'  # 项目名称，可以根据该项目名查看log
    HOST_TYPE = '正式服'
    HOST_NAME = 'Project A Master 1'
    DEBUG = True


class LoggerConf(object):
    """Config of logger"""
    LOG_DIR = './logs'  # log文件都放在该目录下
    DEFAULT_PATH = '%s/default.log' % LOG_DIR

