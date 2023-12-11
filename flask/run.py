from flask import Flask, request, render_template, jsonify
from elasticsearch import Elasticsearch
import json
import os

app = Flask(__name__)
es = Elasticsearch(["http://localhost:9200"])


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("login.html")


# 处理登录和注册请求
@app.route("/user", methods=["POST"])
def user():
    # 读取user.json文件
    with open("user.json", "r", encoding="utf-8") as f:
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
            with open("user.json", "w", encoding="utf-8") as f:
                json.dump(users, f)
            return jsonify({"status": 1, "msg": "注册成功"})
        else:
            return jsonify({"status": 0, "msg": "用户名已存在"})


@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")


@app.route("/search=<query>", methods=["GET"])
def search_results(query):
    # res = es.search(index="my_index", body={"query": {"match": {"content": query}}})
    # hits = res["hits"]["hits"]
    # return render_template("search_results.html", hits=hits)
    return f"u r searching '{query}'"


if __name__ == "__main__":
    app.run(debug=True)
