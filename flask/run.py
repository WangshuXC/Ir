from flask import Flask, request, render_template, jsonify
from elasticsearch import Elasticsearch
import datetime
import json
import os

app = Flask(__name__)
es = Elasticsearch(hosts="http://elastic:n154Sh+KyweYH-+As92v@127.0.0.1:9200")


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("login.html")


# 处理登录和注册请求
@app.route("/user", methods=["POST"])
def user():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # 读取user.json文件
    with open(os.path.join(BASE_DIR, "user.json"), "r", encoding="utf-8") as f:
        users = json.load(f)

    # 获取表单数据
    username = request.form.get("username")
    password = request.form.get("password")

    # 判断请求类型
    if request.form.get("type") == "login":
        # 登录操作
        if username in users and users[username]["password"] == password:
            return jsonify({"status": 1, "msg": "登录成功"})
        else:
            return jsonify({"status": 0, "msg": "用户名或密码错误"})

    elif request.form.get("type") == "register":
        # 注册操作
        if username not in users:
            # 创建新用户
            users[username] = {"password": password}
            # 更新user.json文件
            with open(os.path.join(BASE_DIR, "user.json"), "w", encoding="utf-8") as f:
                json.dump(users, f)
            return jsonify({"status": 1, "msg": "注册成功"})
        else:
            return jsonify({"status": 0, "msg": "用户名已存在"})


@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "")
    if q:
        now = datetime.datetime.now()
        timestamp = now.strftime("[%d/%b/%Y %H:%M:%S]")
        print(f"{timestamp} 用户搜索了{q}")
        query = {
            "explain": True,
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": [
                        "body",
                        "title",
                        "auth",
                        "appreciation",
                    ],
                }
            },
        }

        data = []

        # 执行查询
        result = es.search(index="data", body=query)

        # 处理查询结果
        for hit in result["hits"]["hits"]:
            data.append(
                {
                    "title": hit["_source"]["title"],
                    "url": hit["_source"]["url"],
                    "content": hit["_source"]["body"],
                    "dynasty": hit["_source"]["dynasty"],
                    "auth": hit["_source"]["auth"],
                }
            )

        return render_template("search_detail.html", q=q, data=data)
    else:
        return render_template("search.html")


# @app.route("/search_detail", methods=["GET"])
# def search_results():
#     query = request.args.get("query", "")
#     return render_template("search_detail.html", query=query)
#     # return f"u r searching '{query}'"


if __name__ == "__main__":
    app.run(debug=True)
