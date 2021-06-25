#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    default_celery.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
"""
from configs.celery_config import DefaultCeleryConfig, create_celery_instance


default_inst = create_celery_instance(
    name='default_celery',
    config=DefaultCeleryConfig)
