from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from control.apps import create_app, db
from control.admin.sn import models

CONFIG = "development"  # 选择生产，开发模式
# 创建 app，并传入配置模式：development / production
app = create_app(CONFIG)
# Flask-script
manager = Manager(app)
# 数据库迁移
Migrate(app, db)
# 给终端脚本工具新增数据迁移的相关命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
