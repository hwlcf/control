#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    celery_config.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from celery import Celery, platforms
from celery.schedules import crontab

from configs import CeleryConf

DEFAULT_QUEUE = 'default.queue'


class BaseCeleryConfig(object):
    """Base configuration for celery.
    Each celery instance configs class will extend from this class
    """
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERYD_CONCURRENCY = 1
    CELERY_ACKS_LATE = True
    CELERY_IGNORE_RESULT = True
    CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_EVENT_QUEUE_EXPIRES = 7200
    CELERY_TIMEZONE = 'UTC'


class DefaultCeleryConfig(BaseCeleryConfig):
    """Default celery configuration for this project"""
    CELERYD_CONCURRENCY = CeleryConf.DEFAULT_CELERY_CONCURRENCE
    CELERY_IMPORTS = (
        'logic.celery_task'
    )
    CELERY_ROUTES = {
        'default_task': {
            'queue': DEFAULT_QUEUE,
            'routing_key': DEFAULT_QUEUE
        },
    }
    CELERY_QUEUES = {
        DEFAULT_QUEUE: {
            'exchange': DEFAULT_QUEUE,
            'exchange_type': 'direct',
            'routing_key': DEFAULT_QUEUE
        }
    }


class ScheduleCeleryConfig(BaseCeleryConfig):
    """
    Schedule celery configuration for this project.
    All schedule tasks run in default celery queue.
    """
    # 使用本地时间
    CELERY_ENABLE_UTC = False
    CELERY_TIMEZONE = 'Asia/Shanghai'
    # 定时任务写入配置
    CELERYBEAT_SCHEDULE = {
        'default_task': {
            'task': 'sync_gateway_status',
            'schedule': crontab(minute='*/5'),
            'options': {
                'queue': DEFAULT_QUEUE,
                'routing_key': DEFAULT_QUEUE,
                'exchange': DEFAULT_QUEUE,
                'exchange_type': 'direct'
            }
        },
    }


def create_celery_instance(name, config, broker=CeleryConf.DEFAULT_BROKER_URL):
    """
    创建Celery实例

    Args:
        name: celery名
        config: celery的配置
        broker: celery的broker

    Returns:
        celery_instance: celery实例

    """
    inst = Celery(name, broker=broker)
    inst.config_from_object(config)
    platforms.C_FORCE_ROOT = True  # running celery worker by rooter
    return inst
