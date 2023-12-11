from flask import Flask, request, render_template
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch(["http://localhost:9200"])


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/search", methods=["GET"])
def search():
    # query = request.args.get("query")
    # res = es.search(index="my_index", body={"query": {"match": {"content": query}}})
    # hits = res["hits"]["hits"]
    # return render_template("search.html", hits=hits)
    return render_template("search.html")


@app.route("/search=<query>", methods=["GET"])
def search_results(query):
    res = es.search(index="my_index", body={"query": {"match": {"content": query}}})
    hits = res["hits"]["hits"]
    return render_template("search_results.html", hits=hits)


if __name__ == "__main__":
    app.run(debug=True)
