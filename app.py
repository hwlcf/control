#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
import json
import traceback
from collections import OrderedDict

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_login import LoginManager

from cache import _r
from configs import AppConf, ALLOW_HOST_DOMAINS, API_WHITE_LIST, RedisConf
from logic.flask_extension import ApiMonitor, ReferrerChecker, \
    MongoSessionInterface, LoginManagerLoader
from utils.logger import logger


def get_remote_address():
    forward_for = request.headers.get('X-Forward-For', '')
    if not forward_for:
        return '127.0.0.1'
    return forward_for.split(',')[0].strip()


# Init Flask app
app = Flask(__name__)
app.view_functions = OrderedDict()  # 重新初始化view_functions，方便生成wiki
app.debug = AppConf.DEBUG
app.session_cookie_name = AppConf.SESSION_COOKIE_NAME
app.secret_key = AppConf.SECRET_KEY
app.config['SESSION_COOKIE_DOMAIN'] = AppConf.SESSION_COOKIE_DOMAIN
app.config['REMEMBER_COOKIE_DOMAIN'] = AppConf.SESSION_COOKIE_DOMAIN

# Init Flask Limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri=RedisConf.URL
)
login_limiter = limiter.shared_limit(
    AppConf.LOGIN_API_LIMITER_STR, scope='login'
)


# register blueprint
if AppConf.OPEN_PRODUCT_API:
    from api import api
    api_monitor = ApiMonitor(redis=_r, logger=logger)
    api_monitor.init_app(api)
    referrer_checker = ReferrerChecker(
        ALLOW_HOST_DOMAINS,
        API_WHITE_LIST
    )
    referrer_checker.init_app(api)
    app.register_blueprint(api, url_prefix='/api')

# Init login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.token_loader(LoginManagerLoader.load_user)
login_manager.user_loader(LoginManagerLoader.load_user)
login_manager.request_loader(LoginManagerLoader.request_callback)
login_manager.unauthorized_handler(LoginManagerLoader.unauthorized)
app.session_interface = MongoSessionInterface()


@app.errorhandler(400)
def handle_400(e):
    """捕获abort(400)错误"""
    rsp = {
        'msg': 'Bad Request',
        'err': 10
    }
    if isinstance(e.description, int):
        rsp['err'] = e.description
    if isinstance(e.description, dict):
        rsp.update(e.description)
    return jsonify(**rsp), 400


@app.errorhandler(401)
def handle_401(e):
    rsp = {
        'msg': 'Unauthorized',
        'err': 20
    }
    if isinstance(e.description, int):
        rsp['err'] = e.description
    elif isinstance(e.description, dict):
        rsp.update(e.description)
    return jsonify(**rsp), 401


@app.errorhandler(403)
def handle_403(e):
    rsp = {
        'err': 400,
        'msg': 'Forbidden'
    }
    if isinstance(e.description, int):
        rsp['err'] = e.description
    return jsonify(**rsp), 403


@app.errorhandler(404)
def handle_404(e):
    rsp = {
        'msg': 'Not Found',
        'err': 50
    }
    if isinstance(e.description, dict):
        rsp.update(e.description)
    return jsonify(**rsp), 404


@app.errorhandler(429)
def handle_429(e):
    rsp = {
        'msg': 'Too Many Requests',
        'err': 30
    }
    logger.error('Too many requests at ip: %s' % get_remote_address())
    return jsonify(**rsp), 429


@app.errorhandler(Exception)
def handle_exception(e):
    """Called when exception occurred"""
    traceback.print_exc()
    logger.error(traceback.format_exc())
    return jsonify(), 500


@app.after_request
def after_request_callback(response):
    """Process after request"""
    try:
        if response.status_code in (400, 403, 404, 500, 503):
            method = request.method
            if method in ('POST', 'PUT'):
                params = request.form.to_dict()
            else:
                params = request.args.to_dict()
            rsp_data = str(response.data, encoding='utf-8')
            try:
                rsp_data = json.loads(rsp_data)
            except:
                pass

            log_data = {
                'msg': '请求%s' % response.status_code,
                'response': {
                    'status_code': response.status_code,
                    'data': rsp_data
                },
                'request': {
                    'params': params,
                    'method': request.method,
                    'url': request.url
                }
            }
            logger.warning(log_data)
    except:
        logger.error(traceback.format_exc())
    return response
