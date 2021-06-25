from flask import Blueprint, render_template, current_app, request, jsonify
from control.utils.response_code import RET

user_blu = Blueprint("user", __name__, url_prefix='/user')


@user_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('user/favicon.ico')


@user_blu.route('/index')
def index():
    return render_template('user/index.html')


# 用户列表分页查询
@user_blu.route("/user_list", methods=["GET", "POST"])
def user_list():
    from control.admin.sn.models import User
    """ａｊａｘ请求用户列表数据"""
    # 1 接收参数，前端发送通过ｇｅｔ参数发送
    data_dict = request.args
    page = data_dict.get("page", 1)  # 当前页码
    # print(page, cid)
    # 允许前端指定每一页的数据量，默认为十
    per_page = data_dict.get("per_page", 10)

    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 2 获取
    try:
        paginate = User.query.filter().order_by(User.id.desc()).paginate(page, per_page, False)
        # 获取查询出来的数据[items是一个列表，列表中的每一个成员都是模型对象]
        items = paginate.items
        # 获取到总页数
        total_page = paginate.pages
        current_page = paginate.page

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    # 3. 返回数据之前需要把每一个模型对象转换成字典格式，因为js不识别python的模型对象
    new_dict_list = []
    for news in items:
        new_dict_list.append(news.to_dict())

    # 4 返回结果
    return jsonify(errno=RET.OK, msg="OK",
                   totalPage=total_page,
                   currentPage=current_page,
                   userList=new_dict_list,
                   )
