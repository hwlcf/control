# -*- coding: utf-8 -*-
"""
    flask_extension
    ~~~~~~~
"""
import sys

from bson import ObjectId
from datetime import datetime
from flask import g, request, jsonify, session as flask_session, abort
from flask_login import UserMixin
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature
from werkzeug.datastructures import CallbackDict


class ApiMonitor(object):
    """Api monitor"""
    def __init__(self, redis=None, logger=None):
        """
        :param redis: Redis链接
        :param logger: logger输出实例
        """
        self.redis = redis
        self.logger = logger

    def init_app(self, app):
        """初始化app
        :param app: `Flask`实例或`Blueprint`实例
        """
        app.before_request(self.before_logger)
        app.after_request(self.after_logger)

    @staticmethod
    def cache_key(request_id):
        """生成redis key
        :param request_id:
        :return key:
        """
        key = 'request_id:%s' % request_id
        return key

    def before_logger(self):
        """before request logger"""
        g.request_id = str(ObjectId())
        endpoint = request.endpoint
        if self.logger:
            self.logger.info(
                '%s | %s' % (g.request_id, endpoint))
        if self.redis:
            key = self.cache_key(g.request_id)
            mapping = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'endpoint': endpoint
            }
            self.redis.hmset(key, mapping)
            self.redis.expire(key, 3600*24*7)
        return

    def after_logger(self, response):
        """after request logger"""
        try:
            request_id = g.request_id
        except AttributeError:
            sys.stderr.write('Get request id from `flask.g` failed\n')
            return response
        if self.logger:
            self.logger.info('%s | end' % request_id)
        if self.redis:
            key = self.cache_key(request_id)
            self.redis.delete(key)
        return response


class ReferrerChecker(object):
    """校验referrer"""

    def __init__(self, allow_domains, white_list=None, err=412):
        """
        :param allow_domains: 支持的referrer域名列表(如果为空，则不进行校验)
        :param white_list: flask endpoint白名单列表
        :param err: 校验失败返回的错误码
        """
        self.allow_domains = allow_domains
        self.white_list = white_list
        self.err = err

    def init_app(self, app):
        """初始化app
        :param app: `Flask`实例或`Blueprint`实例
        """
        app.before_request(self.check_referrer)

    def check_referrer(self):
        """校验referrer"""
        if not self.allow_domains:
            return None
        if request.endpoint in self.white_list:
            # 不检查referrer
            return None
        rsp = jsonify(stat=0, err=self.err, msg='Forbidden')

        referrer = request.referrer
        if referrer is None:
            return rsp, 403
        if referrer.startswith('http://'):
            referrer = referrer[7:]
        elif referrer.startswith('https://'):
            referrer = referrer[8:]
        else:
            return rsp, 403

        referrer_domain = referrer.split('/')[0]
        if referrer_domain not in self.allow_domains:
            return rsp, 403

        return None


# ----------------------------------------------
# 重载LoginManager相关的类型，自定义Session管理
# ----------------------------------------------
class MongoSession(CallbackDict, SessionMixin):
    """重载CallbackDict"""
    def __init__(self, initial=None, sid=None, channel=None, status=20):
        CallbackDict.__init__(self, initial)
        self.sid = sid
        self.channel = channel
        self.status = status


class MongoSessionInterface(SecureCookieSessionInterface):
    """Extend default session interface to store and get session from mongodb.
    We just override open_session and save_session functions.
    See: pymongo.sessions.SecureCookieSessionInterface
    Notice:
    flask的session结构为:
    * `flask_session` - 当前flask的session结构
        * `sid` - 从account_session同步过来
        * `status` - 登录时判断
        * `channel` - 从account_session同步过来
        * `...`

    * `account_session` - 账户中心的session结构
        * `sid`
        * `status`
        * `channel`
        * `indi_user_id` - 个人用户id
    """
    session_class = MongoSession
    canary_key = 'canary:'

    @staticmethod
    def get_session_val(session_cookie_name):
        """获取session值"""
        val = request.cookies.get(session_cookie_name) \
            or request.headers.get(session_cookie_name) \
            or request.form.get(session_cookie_name) \
            or request.args.get(session_cookie_name)
        return val

    def open_session(self, app, request):
        """打开session"""
        s = URLSafeTimedSerializer(app.secret_key, 'cookie-session')
        # 获取session
        smart_voice_val = self.get_session_val(app.session_cookie_name)

        try:
            if smart_voice_val:
                smart_voice_data = s.loads(smart_voice_val)
            else:
                smart_voice_data = {}
            session_data = smart_voice_data
            kwargs = {}
            return self.session_class(session_data, **kwargs)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            response.delete_cookie(app.session_cookie_name,
                                   domain=domain, path=path)
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)

        # Notice: session.channel 需要在登录的时候赋值

        s = URLSafeTimedSerializer(app.secret_key, 'cookie-session')
        # Notice: 把数据转换成基本类型数据
        dumps_data = dict(session)
        for key, value in dumps_data.items():
            if not isinstance(value, (int, str, bytes, float)):
                dumps_data[key] = str(value)

        val = s.dumps(dumps_data)

        # set cookies
        response.set_cookie(app.session_cookie_name, val,
                            expires=expires,
                            httponly=httponly,
                            domain=domain,
                            path=path,
                            secure=secure)


class LoginManagerLoader(object):
    """定义LoginManger的loader"""

    @classmethod
    def load_user(cls, user_id):
        """加载user"""
        return cls._load_user()

    @classmethod
    def request_callback(cls, request):
        """
        Sometimes you want to login users without using cookies, such as using
        header values or an api key passed as a query argument. In these cases,
        you should use the request_loader callback. This callback should behave
        the same as your user_loader callback, except that it accepts the Flask
        request instead of a user_id

        :param request: Flask Request object
        :return user: User object or None

        """
        return cls._load_user()

    @classmethod
    def _load_user(cls):
        """统一加载user的入口"""
        # 这里装载你的用户信息
        pass

        return cls.LoginUser()

    @classmethod
    def unauthorized(cls):
        """
        验证失败
        :return:
        """
        abort(401, flask_session.status)

    class LoginUser(UserMixin):
        """初始化current_user
        * `client_id` (str) - 用户id
        * `user_id` (str) - 员工id
        """

        def __init__(self, **kwargs):
            UserMixin.__init__(self)
            for k, v in kwargs.items():
                self.__setattr__(k, v)

        def __getitem__(self, item):
            return self.__getattribute__(item)

        def __contains__(self, key):
            return key in self.__dict__

        def get_id(self):
            return self._id
