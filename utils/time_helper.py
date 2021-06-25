#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    time_helper.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description of this file
    
    :author: Zhidong :)
    :copyright: (c) 2018, Tungee
    :date created: 2018-03-20
    
"""
import time
from datetime import datetime, timedelta

from calendar import timegm, isleap, monthrange


def utc2local(utc_dt):
    """Convert utc datetime to local datetime"""
    return datetime.fromtimestamp(timegm(utc_dt.timetuple()))


def datetime2timestamp(dt):
    return int(timegm(dt.timetuple()) * 1000 + dt.microsecond / 1e3)


def timestamp2datetime(stamp, to_local=False):
    dt = datetime.utcfromtimestamp(stamp / 1e3)
    if to_local:
        return utc2local(dt)
    return dt


def datetime2string(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def local2utc(dt):
    """Convert local time string to utc datetime"""
    return datetime.utcfromtimestamp(time.mktime(dt.timetuple()))


def string2datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def cal_time_range(dt):
    """
    计算时长(运营系统使用)
    :param dt:
    :return:
    """
    total_days = (datetime.utcnow() - dt).days
    years = total_days / 365
    months = total_days % 365 / 30
    days = (total_days % 365) % 30
    if years > 0:
        if months > 0:
            if days > 0:
                time_range = u'%s年%s个月%s天' % (years, months, days)
            else:
                time_range = u'%s年%s个月' % (years, months)
        else:
            if days > 0:
                time_range = u'%s年%s天' % (years, days)
            else:
                time_range = u'%s年' % years
    else:
        if months > 0:
            if days > 0:
                time_range = u'%s个月%s天' % (months, days)
            else:
                time_range = u'%s个月' % months
        else:
            if days > 0:
                time_range = u'%s天' % days
            else:
                time_range = u'不足1天'

    return time_range


def time_add_months(time_begin, months):
    """ 添加月份"""
    target_year = time_begin.year
    target_month = time_begin.month
    target_year += months / 12
    target_month += months % 12
    if target_month > 12:
        target_month -= 12
        target_year += 1

    # 计算目标月份的最大月份
    begin_max_day = monthrange(time_begin.year, time_begin.month)[1]
    target_max_day = monthrange(target_year, target_month)[1]

    if time_begin.day == begin_max_day:
        # 如果当前天数是当月的最大天数，则目标月份使用最大天数
        target_day = target_max_day
    else:
        target_day = min(time_begin.day, target_max_day)

    return datetime(target_year, target_month, target_day)


def get_next_month_same_day(day, date_begin=None):
    """ 获取下个月同一天(如果没有同一天，则获取下下个余额的第一天)"""
    if date_begin is not None:
        now = date_begin
    else:
        now = datetime.now()
        now = datetime(now.year, now.month, now.day)

    # 获取下个月
    next_year = now.year
    next_month = now.month + 1
    if next_month > 12:
        next_year += 1
        next_month -= 12

    next_month_days = monthrange(next_year, next_month)[1]

    if day > next_month_days:
        date = datetime(next_year, next_month, next_month_days) + timedelta(1)
    else:
        date = datetime(next_year, next_month, day)

    return date


def get_date_list(date_begin, date_end, fmt='%Y-%m-%d'):
    """ 获取日期列表"""
    time_begin = datetime.strptime(date_begin, fmt)
    time_end = datetime.strptime(date_end, fmt)

    time_tmp = time_begin
    date_list = list()
    while time_tmp <= time_end:
        date_list.append(time_tmp.strftime(fmt))
        time_tmp += timedelta(days=1)

    return date_list


def time_countdown(rt):
    """ 回收时间倒计时"""
    now = datetime.utcnow()
    if rt < datetime.utcnow():
        rt = now
    delta = rt - now
    days = int(delta.total_seconds() / (3600 * 24))
    hours = int((delta.total_seconds() % (3600 * 24)) / 3600)
    if days > 0:
        rt_str = '%s天' % days
    elif hours > 0:
        rt_str = '%s小时' % hours
    else:
        rt_str = '1小时'

    return rt_str
