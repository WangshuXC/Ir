from flask import Flask, request, render_template, jsonify
from elasticsearch import Elasticsearch
import datetime
import json
import os

app = Flask(__name__)
es = Elasticsearch(hosts="http://elastic:n154Sh+KyweYH-+As92v@127.0.0.1:9200")


def generate_query(q):
    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": q,
                            "fields": [
                                "body",
                                "title",
                                "auth",
                            ],
                        }
                    },
                    {
                        "bool": {
                            "should": [
                                {"match_phrase": {"body": q}},
                                {"match_phrase": {"title": q}},
                                {"match_phrase": {"auth": q}},
                            ]
                        }
                    },
                ]
            }
        },
        "highlight": {
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"],
            "fields": {"body": {}, "title": {}, "auth": {}, "appreciation": {}},
        },
    }


def generate_custom_query(q1, q2, q3):
    query = {
        "query": {"bool": {"must": [], "must_not": []}},
        "highlight": {
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"],
            "fields": {"body": {}, "title": {}, "auth": {}, "appreciation": {}},
        },
    }

    if q1:
        query["query"]["bool"]["must"].append(
            {"match": {"body": {"query": q1, "operator": "or"}}}
        )
        query["query"]["bool"]["must"].append(
            {"match": {"title": {"query": q1, "operator": "or"}}}
        )
        query["query"]["bool"]["must"].append(
            {"match": {"auth": {"query": q1, "operator": "or"}}}
        )

    if q2:
        query["query"]["bool"]["must"].append({"match_phrase": {"body": q2}})
        query["query"]["bool"]["must"].append({"match_phrase": {"title": q2}})
        query["query"]["bool"]["must"].append({"match_phrase": {"auth": q2}})

    if q3:
        query["query"]["bool"]["must_not"].append(
            {"match": {"body": {"query": q3, "operator": "or"}}}
        )
        query["query"]["bool"]["must_not"].append(
            {"match": {"title": {"query": q3, "operator": "or"}}}
        )
        query["query"]["bool"]["must_not"].append(
            {"match": {"auth": {"query": q3, "operator": "or"}}}
        )

    return query


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
    q1 = request.args.get("q1", "")
    q2 = request.args.get("q2", "")
    q3 = request.args.get("q3", "")
    if q:
        now = datetime.datetime.now()
        timestamp = now.strftime("[%d/%b/%Y %H:%M:%S]")
        user_ip = request.remote_addr
        print(f"{user_ip} - - {timestamp} [普通搜索]了 ‘{q}’ -")
        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": q,
                                "fields": [
                                    "body",
                                    "title",
                                    "auth",
                                ],
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {"match_phrase": {"body": q}},
                                    {"match_phrase": {"title": q}},
                                    {"match_phrase": {"auth": q}},
                                ]
                            }
                        },
                    ]
                }
            },
            "highlight": {
                "pre_tags": ["<strong>"],
                "post_tags": ["</strong>"],
                "fields": {"body": {}, "title": {}, "auth": {}, "appreciation": {}},
            },
        }

        data = []

        # 执行查询
        result = es.search(index="data", body=query)

        # 处理查询结果
        for hit in result["hits"]["hits"]:
            highlight = hit.get("highlight", {})
            body_highlight = highlight.get("body", [])
            title_highlight = highlight.get("title", [])
            auth_highlight = highlight.get("auth", [])
            appreciation_highlight = highlight.get("appreciation", [])

            data.append(
                {
                    "title": hit["_source"]["title"],
                    "url": hit["_source"]["url"],
                    "content": hit["_source"]["body"],
                    "dynasty": hit["_source"]["dynasty"],
                    "auth": hit["_source"]["auth"],
                    "body_highlight": body_highlight,
                    "title_highlight": title_highlight,
                    "auth_highlight": auth_highlight,
                    "appreciation_highlight": appreciation_highlight,
                }
            )

        return render_template("search_detail.html", q=q, data=data)
    else:
        return render_template("search.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
