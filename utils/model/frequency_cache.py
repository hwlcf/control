#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    frequency_cache.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
"""
from pymongo.collection import Collection
from pymongo.operations import IndexModel
from pymongo.read_preferences import ReadPreference

from . import _db


class FrequencyCache(object):
    """
    Log频率限制缓存
    """
    COL_NAME = 'frequency_cache'

    p_col = Collection(
        _db, COL_NAME,
        read_preference=ReadPreference.PRIMARY_PREFERRED
    )
    s_col = Collection(
        _db, COL_NAME,
        read_preference=ReadPreference.SECONDARY_PREFERRED
    )

    class Field(object):
        _id = '_id'
        data = 'data'
        time = 'time'

    try:
        indexes = list()
        indexes.append(
            IndexModel(Field.time, expireAfterSeconds=3600)
        )
        p_col.create_indexes(indexes)
    except Exception as e:
        pass

