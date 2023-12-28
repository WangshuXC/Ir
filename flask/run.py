from flask import Flask, request, session, render_template, jsonify
from elasticsearch import Elasticsearch
from collections import Counter
import datetime
import json
import math
import os
import re

app = Flask(__name__)
app.secret_key = "lxcSoHandsome"
index_name = "shici"
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


def generate_custom_query(q1, q2, q3, q2t, q2a, q2b):
    query = {
        "query": {"bool": {"must": [], "must_not": [], "should": []}},
        "highlight": {
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"],
            "fields": {"body": {}, "title": {}, "auth": {}, "appreciation": {}},
        },
    }

    if q1:
        keywords = q1.split()

        for keyword in keywords:
            query["query"]["bool"]["should"].extend(
                [
                    {"match_phrase": {"body": keyword}},
                    {"match_phrase": {"title": keyword}},
                    {"match_phrase": {"auth": keyword}},
                ]
            )

    if q2:
        keywords = q2.split()
        if q2t == "true" or q2a == "true" or q2b == "true":
            pass
        else:
            for keyword in keywords:
                query["query"]["bool"]["must"].extend(
                    [
                        {"match_phrase": {"body": q2}},
                    ]
                )

        if q2b == "true":
            for keyword in keywords:
                query["query"]["bool"]["must"].extend(
                    [
                        {"match_phrase": {"body": q2}},
                    ]
                )

        if q2a == "ture":
            for keyword in keywords:
                query["query"]["bool"]["must"].extend(
                    [
                        {"match_phrase": {"auth": q2}},
                    ]
                )

        if q2t == "ture":
            for keyword in keywords:
                query["query"]["bool"]["must"].extend(
                    [
                        {"match_phrase": {"title": q2}},
                    ]
                )

    if q3:
        keywords = q3.split()

        for keyword in keywords:
            query["query"]["bool"]["must_not"].extend(
                [
                    {"match_phrase": {"body": q3}},
                    {"match_phrase": {"auth": q3}},
                    {"match_phrase": {"title": q3}},
                ]
            )

    return query


def re_sort(results, history):
    def tokenize(text):
        text = re.sub(r"<.*?>", "", text)
        tokens = text.split()
        merged_text = " ".join(tokens)
        return merged_text

    def cosine_similarity(a, b):
        a_tokens = tokenize(a)
        b_tokens = tokenize(b)
        a_vector = Counter(a_tokens)
        b_vector = Counter(b_tokens)

        intersection = set(a_vector.keys()) & set(b_vector.keys())
        dot_product = sum(a_vector[x] * b_vector[x] for x in intersection)

        norm_a = math.sqrt(sum(a_vector[x] ** 2 for x in a_vector))
        norm_b = math.sqrt(sum(b_vector[x] ** 2 for x in b_vector))

        similarity = dot_product / (norm_a * norm_b)
        return similarity

    def calculate_similarity(search_results, search_history):
        similarities = []
        for result in search_results:
            r_text = result["title"] + " " + result["auth"] + " " + result["content"]
            for history in search_history:
                similarity = cosine_similarity(r_text, history)
                similarities.append(similarity)

        return similarities

    def sort_results(search_results, search_history):
        similarities = calculate_similarity(search_results, search_history)
        for i, result in enumerate(search_results):
            score_weight = result["score"] * 0.1
            similarity_weight = similarities[i] * 10
            pagerank_weight = result["pagerank"] * 1000000
            total_weight = score_weight + similarity_weight + pagerank_weight
            result["total_weight"] = total_weight
        sorted_results = sorted(
            search_results, key=lambda x: x["total_weight"], reverse=True
        )
        return sorted_results

    return sort_results(results, history)


def recommendation_query(history):
    if history:
        query = {
            "query": {
                "more_like_this": {
                    "fields": ["body", "auth", "title"],
                    "like": history,
                    "min_term_freq": 1,
                    "max_query_terms": 12,
                }
            }
        }
    else:
        query = {
            "query": {
                "more_like_this": {
                    "fields": ["auth"],
                    "like": ["李白", "杜甫", "辛弃疾"],
                    "min_term_freq": 1,
                    "max_query_terms": 12,
                }
            }
        }
    recommendation = es.search(index=index_name, body=query)
    rec = []
    for hit in recommendation["hits"]["hits"]:
        rec.append(
            {
                "title": hit["_source"]["title"],
                "url": hit["_source"]["url"],
                "content": hit["_source"]["body"],
                "dynasty": hit["_source"]["dynasty"],
                "auth": hit["_source"]["auth"],
            }
        )
    return rec


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("login.html")


# 处理登录和注册请求
@app.route("/user", methods=["POST"])
def user():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    user_json_path = os.path.join(BASE_DIR, "user.json")
    if not os.path.exists(user_json_path):
        # 创建目录和文件
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(user_json_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
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
            session["username"] = username
            return jsonify({"status": 1, "msg": "登录成功"})
        else:
            return jsonify({"status": 0, "msg": "用户名或密码错误"})

    elif request.form.get("type") == "register":
        # 注册操作
        if username not in users:
            # 创建新用户
            users[username] = {"password": password, "history": []}
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
    q2t = request.args.get("q2t", "")
    q2a = request.args.get("q2a", "")
    q2b = request.args.get("q2b", "")

    q3 = request.args.get("q3", "")

    # 读取user.json文件
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(BASE_DIR, "user.json"), "r", encoding="utf-8") as f:
        users = json.load(f)

    username = session.get("username")
    history = users[username]["history"]
    recommendation = recommendation_query(history)

    now = datetime.datetime.now()
    timestamp = now.strftime("[%d/%b/%Y %H:%M:%S]")
    user_ip = request.remote_addr

    data = []

    if q and not (q1 or q2 or q3):
        print(f"{user_ip} - - {timestamp} [普通搜索]了 ‘{q}’ -")

        query = generate_query(q)

        # 执行查询
        result = es.search(index=index_name, body=query)

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
                    "score": hit["_score"],
                    "pagerank": hit["_source"]["pagerank"],
                    "body_highlight": body_highlight,
                    "title_highlight": title_highlight,
                    "auth_highlight": auth_highlight,
                    "appreciation_highlight": appreciation_highlight,
                }
            )

        if history:
            data = re_sort(data, history)

        users[username]["history"].append(q)
        # 更新user.json文件
        with open(os.path.join(BASE_DIR, "user.json"), "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return render_template("search_detail.html", q=q, data=data, rec=recommendation)
    elif q1 or q2 or q3:
        print(f"{user_ip} - - {timestamp} [高级搜索]了 包含任意‘{q1}’, 包含完整‘{q2}’, 不包含‘{q3}’ -")

        query = generate_custom_query(q1, q2, q3, q2t, q2a, q2b)
        # 执行查询
        result = es.search(index=index_name, body=query)

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
                    "score": hit["_score"],
                    "pagerank": hit["_source"]["pagerank"],
                    "body_highlight": body_highlight,
                    "title_highlight": title_highlight,
                    "auth_highlight": auth_highlight,
                    "appreciation_highlight": appreciation_highlight,
                }
            )

        if history:
            data = re_sort(data, history)

        if q1:
            items = q1.split()
            for item in items:
                users[username]["history"].append(item)

        if q2:
            items = q2.split()
            for item in items:
                users[username]["history"].append(item)
        # 更新user.json文件
        with open(os.path.join(BASE_DIR, "user.json"), "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)

        return render_template(
            "search_detail.html",
            q1=q1,
            q2=q2,
            q2t=q2t,
            q2a=q2a,
            q2b=q2b,
            q3=q3,
            data=data,
            rec=recommendation,
        )
    else:
        return render_template("search.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
