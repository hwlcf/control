import logging
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
# from flask_session import Session
import control.admin.user.views
from control.config import Config, config
import pymysql

pymysql.install_as_MySQLdb()

redis_store = None
# 创建mysql操作对象
db = SQLAlchemy()


# 上面两个都是通过设置好全局变量，然后在ｍａｎａｇｅｒ直接导入

def setup_log(config_name):
    """配置日志"""
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("C:\\Users\\huang\\Desktop\\py_control\\logs\\log",
                                           maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """通过传入不同的配置名字，初始化其对应配置的应用实例"""

    # 配置项目日志
    setup_log(config_name)
    app = Flask(__name__)
    # 根据配置文件中的字典查找对应的配置类
    Config = config[config_name]

    # 加载配置类到flask项目中
    app.config.from_object(Config)
    # 配置数据库
    global db
    db.init_app(app)
    # 配置redis
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    # 开启csrf保护
    CSRFProtect(app)

    # 注册蓝图
    from control.admin.user.views import index_blu
    from control.admin.sn.views import sn_blu
    app.register_blueprint(index_blu)
    app.register_blueprint(sn_blu)

    return app
