# -*- coding: utf-8 -*-

import re
import uuid
from copy import deepcopy
from .logger import logger
from werkzeug.exceptions import abort


def check_phone(phone):
    return bool(re.match(
        r'^134[0-8]\d{7}$|'
        r'^13[^4]\d{8}$|'
        r'^14[5-9]\d{8}$|'
        r'^15[^4]\d{8}$|'
        r'^16[6]\d{8}$|'
        r'^17[0-8]\d{8}$|'
        r'^18[\d]{9}$|'
        r'^19[8,9]\d{8}$', phone))


def check_email(email):
    if len(email) > 7:
        if re.match(
            r'[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', email
        ) != None:
            return True

    return False


def abort_400(err_msg, err=10):
    """
    抛出400 Param Error 错误
    :param err_msg: 错误信息
    :param err: 错误码
    :return:
    """
    abort(400, {'msg': err_msg['msg'], 'err': err,
                'err_code': err_msg['err_code']})


def abort_404(err_msg):
    """
    抛出404 Not Found 错误
    :param err_msg: 错误信息
    """
    abort(404, {'msg': err_msg['msg'], 'err_code': err_msg['err_code']})


def logic_generate_error_msg(msg, **kwargs):
    payload = deepcopy(kwargs)
    uid = str(uuid.uuid4())[:8]
    error_msg = {
        'msg': msg,
        'err_code': uid
    }
    log = payload.pop('log', True)
    if log:
        payload.update(error_msg)
        # stacks = inspect.stack()
        # if len(stacks) > 1:
        #     frame = stacks[1]
        # else:
        #     frame = stacks[0]
        # inspect.Signature()
        # payload['source'] = '%s:lineno:%s#func:%s' % (frame.filename, frame.lineno, frame.function)
        logger.info(payload)
    return error_msg