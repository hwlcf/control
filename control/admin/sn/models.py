from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# from control.apps import db
from control.apps import db


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel, db.Model):
    """用户"""
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)  # 自增id
    sn_number = db.Column(db.String(128), unique=True, nullable=False)  # sn
    version = db.Column(db.String(128), nullable=False)  # 系统版本
    model_number = db.Column(db.String(128), unique=True, nullable=False)  # 手机型号
    last_login = db.Column(db.DateTime, default=datetime.now)  # 最后一次登录时间
    is_usable = db.Column(db.Boolean, default=True)  # sn是否可用

    def to_dict(self):
        """将对象信息转换为字典数据"""

        resp_dict = {
            "id": self.id,
            "sn_number": self.sn_number,
            "version": self.version,
            "model_number": self.model_number,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S"),
            "is_usable": self.is_usable,
        }

        return resp_dict
