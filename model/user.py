#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    user.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from flask_login import UserMixin
from pymongo.collection import Collection
from pymongo.read_preferences import ReadPreference

from . import db


class User(UserMixin):
    """
    * `_id` (str)
    * `phone` (str)
    * `name` (str)
    * `gender` (int)
        * `0` - Unknown
        * `1` - Male
        * `2` - Female

    ---
    """
    COL_NAME = 'user'
    p_col = Collection(
        db, COL_NAME, read_preference=ReadPreference.PRIMARY_PREFERRED
    )
    s_col = Collection(
        db, COL_NAME, read_preference=ReadPreference.SECONDARY_PREFERRED
    )

    class Field(object):
        _id = '_id'
        phone = 'phone'
        name = 'name'
        gender = 'gender'

    class Gender(object):
        unknown = 0
        male = 1
        female = 2

