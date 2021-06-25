#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    celery_task.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
"""
from configs.default_celery import default_inst
from logic import celery_logging_decorator


@default_inst.task(name='default_task')
@celery_logging_decorator
def default_task():
    pass

