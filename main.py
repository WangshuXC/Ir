import os
import json
import threading
import subprocess
from elasticsearch import Elasticsearch

# Elasticsearch配置
username = "elastic"
password = "n154Sh+KyweYH-+As92v"
index_name = "data"


def index_build():
    # 创建Elasticsearch客户端
    es = Elasticsearch(hosts="http://elastic:n154Sh+KyweYH-+As92v@127.0.0.1:9200")

    # 加载数据文件
    with open("data_pagerank.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 创建索引
    if not es.indices.exists(index=index_name):
        doc = {
            "settings": {
                "analysis": {
                    "analyzer": "ik_max_word",
                    "search_analyzer": "ik_max_word",
                }
            },
            "mappings": {
                "properties": {
                    "url": {"type": "text"},
                    "auth": {"type": "text"},
                    "dynasty": {"type": "text"},
                    "type": {"type": "text"},
                    "title": {"type": "text"},
                    "body": {"type": "text"},
                    "translation": {"type": "text"},
                    "appreciation": {"type": "text"},
                }
            },
        }
        es.indices.create(index=index_name, body=doc)

    # 构建文档并索引
    for item in data:
        es.index(index=index_name, id=item["id"], body=item)

    # 刷新索引以使更改生效
    es.indices.refresh(index=index_name)

    print("索引构建完成")


def run_flask():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    flask_dir = os.path.join(current_dir, "flask")
    os.chdir(flask_dir)
    subprocess.run(["python", "run.py"])


def run_elasticsearch():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    elastic_dir = os.path.join(current_dir, "elasticsearch")
    # subprocess.run(["cmd", "/c", "elasticsearch.bat"])
    subprocess.run(
        ["cmd", "/c", "start", "cmd", "/k", "elasticsearch.bat"],
        cwd=os.path.join(elastic_dir, "bin"),
    )


if __name__ == "__main__":
    # 创建两个线程并分别运行对应的函数
    t1 = threading.Thread(target=run_flask)
    t2 = threading.Thread(target=run_elasticsearch)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
