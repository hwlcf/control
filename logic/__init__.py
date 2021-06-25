#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Description of this file

"""
import traceback
from functools import wraps
from utils.logger import logger


def celery_logging_decorator(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e
        return result
    return func_wrapper
