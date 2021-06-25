#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    configs.example.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    拷贝当前文件的配置到configs.py中
    
    :author: Zhidong :)
    :copyright: (c) 2018, Tungee
    :date created: 2018-03-20
    
"""


class ProjectConf(object):
    """Config of project"""
    PROJECT_NAME = 'default'  # 项目名称，可以根据该项目名查看log
    HOST_TYPE = '正式服'
    HOST_NAME = 'Project A Master 1'
    DEBUG = True


class DayuConf(object):
    """Config of ali dayu"""
    URL = 'http://gw.api.taobao.com/router/rest'
    APP_KEY = ''
    SECRET_KEY = ''


class SendcloudConf(object):
    """Config of sendcloud"""
    URL = 'http://sendcloud.sohu.com/webapi/mail.send_template.json'
    DEFAULT_ADDRESS = 'postmaster@no-reply.tungee.com'
    API_KEY = ''
    TRIGGER_API_USER = 'set_email'
    BATCH_API_USER = 'tungee_notification'


class MongoConf(object):
    """Config of Mongodb"""
    HOST = 'localhost:27017'
    DB = 'trace_log'             # 数据库
    IS_AUTH = False     # 是否验证用户
    USER = ''           # 用户名
    PWD = ''            # 密码
    IS_REPLICA = False  # 是否是集群
    REPLICA = ''        # 集群名


class ErrorNotifyConf(object):
    """Config of error notify"""
    # 邮件配置
    EMAIL_ADDRESSES = []
    EMAIL_TEMP = 'tg_error_alert'
    EMAIL_SUBJECT = 'Server Error'

    # 短信配置
    PHONE_NUMBERS = []
    PHONE_TEMP = 'SMS_13085144'
    PHONE_SIGN = '探迹科技'

    REPEAT_COUNT = 3
    INTERVAL_TIME = 3600 * 1


class LoggerConf(object):
    """Config of logger"""
    LOG_DIR = './logs'  # log文件都放在该目录下
    DEFAULT_PATH = '%s/default.log' % LOG_DIR


class OssConf(object):
    """Config of oss"""
    END_POINT = 'oss-cn-shenzhen.aliyuncs.com'
    END_INTERNAL_POINT = 'oss-cn-shenzhen-internal.aliyuncs.com'
    ACCESS_ID = ''
    ACCESS_KEY = ''
    BUCKET = ''


class TCConf(object):
    """Config of TC(Trade Center)"""
    HOST = 'http://localhost:18888'
    PROJECT_ID = 'test'
    SECRET_KEY = ''
