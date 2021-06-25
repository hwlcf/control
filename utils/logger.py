#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    logger.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    logger模块

    如果只是简单的记录log，则使用实例化后的logger，如果需要比较复杂的logger，则可以自己调用
    get_logger()初始化
    
"""
import json
import os
import time
from datetime import datetime
from logging import (
    Filter, INFO, DEBUG,
    Formatter, getLogger, StreamHandler
)
from logging.handlers import TimedRotatingFileHandler
from pymongo import ReturnDocument

from configs import ProjectConf, LoggerConf
from .model.frequency_cache import FrequencyCache


class FrequencyFilter(Filter):
    """ Filter for log frequency
    """

    def __init__(self, name='', prefix=None,
                 repeat_count=3, interval_time=3600):
        """
        :param name: filter名称，默认不填
        :param prefix: 用于区分不同的handler，避免同一个filter被多个handler调用而影响频率
        :param repeat_count: 报错重复的次数
        :param interval_time: 报错间隔时间
        """
        Filter.__init__(self, name=name)
        self._repeat_count = repeat_count
        self._interval_time = interval_time
        self._prefix = prefix

    def filter(self, record):
        """ Filter if the custom log
        """
        if super(FrequencyFilter, self).filter(record) == 0:
            return 0

        # distinguish this error log
        params = [
            record.module,
            record.filename,
            record.funcName,
            str(record.lineno),
            record.levelname
        ]
        if self._prefix:
            params.append(self._prefix)
        key = ','.join(params)

        # get redis value of this key
        cache = FrequencyCache.p_col.find_one_and_update(
            {'_id': key},
            {
                '$inc': {FrequencyCache.Field.data: 1},
                '$setOnInsert': {
                    '_id': key,
                    FrequencyCache.Field.time: datetime.utcnow()
                }
            },
            return_document=ReturnDocument.AFTER,
            upsert=True
        )
        v = cache[FrequencyCache.Field.data]

        if v <= self._repeat_count + 1:
            # will be handled
            return 1
        else:
            return 0


class CustomLogFilter(Filter):
    """ Filter for custom log. If custom log, filter function will return 0.
    """

    def __init__(self, name=''):
        Filter.__init__(self, name=name)

    def filter(self, record):
        """ Filter if the custom log
        """
        if super(CustomLogFilter, self).filter(record) == 0:
            return 0

        # check if custom log
        # we know that custom log record will have `log_name` extra fields
        if hasattr(record, 'log_name'):
            return 0
        return 1


# class SendcloudHandler(Handler):
#     """
#     Sendcloud handler, will send email via sendcloud api.
#     """
#
#     def __init__(self, temp, subject, api_user, addresses):
#         Handler.__init__(self)
#         self._temp = temp
#         self._subject = subject
#         self._api_user = api_user
#         self._addresses = addresses
#
#     def emit(self, record):
#         """
#         Override handler to send email via sendcloud api
#
#         Args:
#             record: LogRecord instance containing log information
#
#         Returns:
#
#         """
#         msg = self.format(record)
#         params = {
#             'type': record.levelname,
#             'location': '%s:%d' % (record.pathname, record.lineno),
#             'module': record.module,
#             'function': record.funcName,
#             'time': datetime.fromtimestamp(
#                 record.created).strftime('%Y-%m-%d %H:%M'),
#             'message': msg.replace('\n', '<br>')
#         }
#
#     def format(self, record):
#         if isinstance(record.msg, dict):
#             line = record.msg
#             line = json.dumps(line, ensure_ascii=False, indent=1)
#         else:
#             line = super(SendcloudHandler, self).format(record)
#
#         return line


# class DayuMessageHandler(Handler):
#     """
#     Dayu Message handler, will send phone message via dayu api.
#     """
#
#     def __init__(self, host_type, numbers, temp, sign):
#         Handler.__init__(self)
#         self._host_type = host_type
#         self._numbers = numbers
#         self._temp = temp
#         self._sign = sign

    # def emit(self, record):
    #     """
    #     Override emit method to send message.
    #
    #     Args:
    #         record: LogRecord instance
    #
    #     """
    #     content = {
    #         'server': self._host_type,
    #         'api': record.msg,
    #     }
    #     try:
    #         dayu.send(
    #             numbers=self._numbers,
    #             template_id=self._temp,
    #             sign_name=self._sign,
    #             content=content)
    #     except Exception:
    #         traceback.print_exc()


# def get_mailer(level=ERROR):
#     # create a sendcloud email handler
#     mailer = SendcloudHandler(
#         ErrorNotifyConf.EMAIL_TEMP,
#         '%s %s' % (ErrorNotifyConf.EMAIL_SUBJECT, ProjectConf.HOST_NAME),
#         SendcloudConf.TRIGGER_API_USER,
#         ErrorNotifyConf.EMAIL_ADDRESSES,
#     )
#     mailer.addFilter(CustomLogFilter())
#     mailer.addFilter(FrequencyFilter(
#         prefix='mailer',
#         repeat_count=ErrorNotifyConf.REPEAT_COUNT,
#         interval_time=ErrorNotifyConf.INTERVAL_TIME))
#
#     mailer.setLevel(level)
#
#     return mailer


# def get_messager(level=ERROR):
#     # create a http message handler
#     messager = DayuMessageHandler(
#         ProjectConf.HOST_NAME,
#         ErrorNotifyConf.PHONE_NUMBERS,
#         ErrorNotifyConf.PHONE_TEMP,
#         ErrorNotifyConf.PHONE_SIGN
#     )
#     messager.addFilter(CustomLogFilter())
#     messager.addFilter(FrequencyFilter(
#         prefix='messager',
#         repeat_count=ErrorNotifyConf.REPEAT_COUNT,
#         interval_time=ErrorNotifyConf.INTERVAL_TIME))
#
#     messager.setLevel(level)
#
#     return messager


class FileFormatter(Formatter):
    """ For recording json format data log
    """

    def __init__(self):
        super(FileFormatter, self).__init__()

    def format(self, record):
        """ Override format function"""
        line = (
            '[{time}]|{level_name}|{pathname}|line:{line_no}|'
            '{function_name}|%s'
        ).format(
            time=self.formatTime(record, self.datefmt),
            level_name=record.levelname,
            pathname=record.pathname,
            line_no=record.lineno,
            function_name=record.funcName
        )
        if isinstance(record.msg, dict):
            s = line % json.dumps(record.msg, ensure_ascii=False)
            # 防止log太大
            if len(s) > 1000:
                s = s[:500] + '......' + s[-500:]
            return s
        else:
            s = line % str(record.msg)
            # 防止log太大
            if len(s) > 1000:
                s = s[:500] + '......' + s[-250:]
            return s


class SpecifyLevelFilter(Filter):
    """输出指定level的log"""
    def __init__(self, level, name=''):
        """
        :param level: 只输出指定level的数据
        :param name:
        """
        Filter.__init__(self, name=name)
        self._level = level

    def filter(self, record):
        """ Filter if the custom log
        """
        if record.lineno == self._level:
            return 1
        return 0



class ConcurrentTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    ConcurrentTimedRotatingFileHandler: A smart replacement for the standard
    TimedRotatingFileHandler, the primary difference being that this handler
    support multiprocessing
    """

    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False):
        super(ConcurrentTimedRotatingFileHandler, self).__init__(
            filename, when=when, interval=interval,
            backupCount=backupCount, encoding=encoding, delay=delay, utc=utc)

    def doRollover(self):
        """
        Overwrite doRollover()
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend

        if os.path.exists(dfn):
            pass
        else:
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)

        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()

        self.rolloverAt = newRolloverAt


def get_logger(name=None, filename=None, when='D', interval=1, backup_count=60,
               notify=True, formatter_args=None):
    """ Get traceback logger
    :param name: logger名称
    :param filename: logger输出文件名（只需要文件名，放在log目录下）
    :param when: 按时间保存的间隔单位
    :param interval: 保存间隔
    :param backup_count: 保存logger文件数量
    :param notify: 是否发送通知(级别为ERROR以上的需要发送短信和邮件通知)
    :param formatter_args: Formatter类参数
    """
    if name:
        log = getLogger(name)
    else:
        log = getLogger(__name__)

    if not filename:
        filename = LoggerConf.DEFAULT_PATH
    else:
        filename = '%s/%s' % (LoggerConf.LOG_DIR, filename)

    # 输出到文件
    if formatter_args:
        formatter = Formatter(*formatter_args)
    else:
        formatter = FileFormatter()
    file_handler = ConcurrentTimedRotatingFileHandler(
        filename,
        when=when,
        interval=interval,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(INFO)
    log.addHandler(file_handler)

    if ProjectConf.DEBUG:
        formatter = FileFormatter()
        stream_handler = StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(DEBUG)
        log.addHandler(stream_handler)
        log.setLevel(DEBUG)

    else:
        log.setLevel(INFO)

    return log


logger = get_logger()
