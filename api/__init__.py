#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Description of this file

"""
from flask import Blueprint


api = Blueprint('/api', __name__)

# 注册模块
from api import (
    user,
)
