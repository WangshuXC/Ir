# HW5 Web搜索引擎  

作业要求：

> 实现本次作业主要有⽹⻚抓取、文本索引、链接分析、查询服务、高级查询、个性化查询⼏个步骤，个性化推荐为扩展内容

本次作业自起始阶段就发布在[WangshuXC/Search_engine](https://github.com/WangshuXC/Search_engine)



## 网页抓取

### 抓取内容

本人抓取的网页为`https://www.gushici.com/`，抓取的内容为网页上所有的诗、词、曲、文言文

以一个抓取到的内容为例来展示每个具体项：

```json
  {
    "id": 53,
    "url": "https://www.gushici.com/t_53",
    "title": "赠汪伦",
    "auth": "李白",
    "auth_id": 618,
    "auth_intro": "李白（701年－762年），字太白，号青莲居士，唐朝浪漫主义诗人，被后人誉为“诗仙”。祖籍陇西成纪(待考)，出生于西域碎叶城，4岁再随父迁至剑南道绵州。李白存世诗文千余篇，有《李太白集》传世。762年病逝，享年61岁。其墓在今安徽当涂，四川江油、湖北安陆有纪念馆。",
    "dynasty": "唐代",
    "type": "诗",
    "body": "<p>李白乘舟将欲行，忽闻岸上踏歌声。</p><p>桃花潭水深千尺，不及汪伦送我情。</p>",
    "translation": "<p>我正乘上小船，刚要解缆出发，忽听岸上传来，悠扬踏歌之声。</p><p>看那桃花潭水，纵然深有千尺，怎能及汪伦送我之情。</p><div><p>参考资料：</p><p>1、张国举．唐诗精华注译评．唐诗：唐诗精华注译评，2010：185-186</p></div>",
    "explanation": "<p>踏歌：唐代一作广为流行的民间歌舞形式，一边唱歌，一边用脚踏地打拍子，可以边走边唱。</p><p>桃花潭：在今安徽泾县西南一百里。《一统志》谓其深不可测。深千尺：诗人用潭水深千尺比喻汪伦与他的友情，运用了夸张的手法（潭深千尺不是实有其事）。不及：不如。</p>",
    "appreciation": "<p>　　用比兴手法，表达了对汪伦深情相送的感激。用“深千尺”的潭水比喻送别之深情，生动而形象，而又加“不及”二字，更增强了诗句的动人力量。这首有明显的民歌风味的诗词自然质朴，清新流畅。诗人用眼前普通的景物作比喻，写出了与友人的真挚情意。</p>",
    "related": [
      "https://www.gushici.com/t_46",
      "https://www.gushici.com/t_100",
      "https://www.gushici.com/t_116",
      "https://www.gushici.com/t_159",
      "https://www.gushici.com/t_166",
      "https://www.gushici.com/t_273",
      "https://www.gushici.com/t_862051",
      "https://www.gushici.com/t_1192921"
    ]
  }
```



### 抓取思路

首先进入到该网站的诗、词、曲、文言文目录页面，即`https://www.gushici.com/p_p_1`到`https://www.gushici.com/p_p_4`

然后分析网页结构，很容易发现该网站的目录页面的页数切换是通过请求api然后动态加载来实现的。

随后自然而然地找到该请求api，发现其格式为`https://www.gushici.com/poetry_list?type={type}&page={page}`，{type}处应填入`诗、词、曲、文言文`其中一项，{page}则为页数。例如我想查询诗目录的第114页，则向`https://www.gushici.com/poetry_list?type=诗&page=114`发送请求。

上述api的返回值是一个json，通过解析、存储这个json，就能轻易地获取到网页的数据。



但是有一个问题，为了后续的**链接分析**过程，还需要找到一些相互关联的网站。为了解决这个问题，我来到了古诗的详情页，以[《赠汪伦》](https://www.gushici.com/t_53)这首诗为例，不难发现其页面中有一个*”猜你喜欢“*板块，这个板块能够链接到其他古诗的详情页，基于此我们就可以抓取相关网页链接来进行链接分析。

![image-20231211190022809](./assets/image-20231211190022809.png)



### 爬虫代码

相关部分在`spider.py`的`spider_index()`和`spider_link(url)`两个函数



代码的运行流程大致如下：

1. 导入所需的库和模块。
2. 定义`spider_index()`函数，用于爬取首页数据。该函数内部定义了一个内部函数`process_page()`，用于处理每一页的数据。`process_page()`函数接收参数url（首页URL）、type（类型，如诗、词、曲等）和num_pages（总页数），并返回一个包含所有数据的列表。
3. 在`spider_index()`函数中，通过不同的URL调用`process_page()`函数，分别爬取诗、词、曲和文言文的数据，并将所有数据合并到`data_list`列表中。
4. 将爬取到的数据写入文件"data.json"中。
5. 定义`spider_link()`函数，用于爬取诗词详情页的链接。该函数使用BeautifulSoup解析网页并获取链接，返回一个包含链接的列表。
6. 使用`retry`装饰器修饰`spider_link()`函数，设置重试次数为3次，每次重试之间的延迟为10秒。

7. 在`if __name__ == "__main__":`语句块中，首先检查是否已经存在"data.json"文件，如果存在则直接跳过爬取步骤，否则调用`spider_index()`函数进行初次爬取。



## 链接分析

在**抓取思路**中我选取了不同链接之间的互相指向来建立链接分析，接下来我就讲述一下如何实现

相关部分在`spider.py`的`add_pagerank()`函数中

```python
def add_pagerank(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data_list = json.load(file)

    G = nx.DiGraph()
    for item in data_list:
        mainlink = item["url"]
        related_links = item.get("related")
        G.add_node(mainlink)
        if related_links is not None:
            for link in related_links:
                G.add_edge(mainlink, link)

    pageranks = nx.pagerank(G)

    for item in data_list:
        url = item["url"]
        item["pagerank"] = pageranks[url]

    with open("data_pagerank.json", "w", encoding="utf-8") as file:
        json.dump(data_list, file, ensure_ascii=False, indent=4)
```

代码十分简单，具体是使用了`networkx`包进行有向图的构建以及计算pagerank

首先是将储存了抓取数据的`data.json`进行读入，将数据加载进内存中。

然后使用`G = nx.DiGraph()`创建一个名为G的图，再遍历整个`data_list`，为每条数据建立结点。如果这个对应的古诗词项没有链接网页就不进行有向边的构建。

然后使用`pageranks = nx.pagerank(G)`，计算整个有向图的pagerank，再用for循环给`data_list`添加一个pagerank的项，最后将添加了链接分析的`data_list`保存为`data_pagerank.json`



## 文本索引

相关部分在`index_build.ipynb`



构建索引首先需要进行对Elasticsearch的连接，这里我使用了python的`Elasticsearch`库，它能够帮助我连接到本地部署的Elasticsearch并且进行一系列的操作

```python
import json
from elasticsearch import Elasticsearch

# Elasticsearch配置
username = "elastic"
password = "n154Sh+KyweYH-+As92v"
index_name = "shici"

# 创建Elasticsearch客户端
es = Elasticsearch(hosts="http://elastic:n154Sh+KyweYH-+As92v@127.0.0.1:9200")
```

`http://elastic:n154Sh+KyweYH-+As92v@127.0.0.1:9200`中的`elasticsearch`是Elasticsearch的用户名，`n154Sh+KyweYH-+As92v`是密码，`9200`是对应开放的端口号

```python
# 加载数据文件
with open("data_pagerank.json", "r", encoding="utf-8") as f:
    data = json.load(f)

    # 创建索引
    if not es.indices.exists(index=index_name):
        doc = {
            'settings': {
                'analysis': {
                    'analyzer': 'ik_max_word',
                    "search_analyzer": 'ik_max_word'
                }
            },
            'mappings':{
                'properties':{
                    'url':{
                        'type': 'text'
                    },
                   'auth':{
                        'type': 'text'
                    },
                    'dynasty': {
                        'type': 'text'
                    },
                    'type': {
                        'type': 'text'
                    },
                    'title':{
                        'type': 'text'
                    },
                    'body': {
                        'type': 'text'
                    },
                    'translation': {
                        'type': 'text'
                    },
                    'appreciation': {
                        'type': 'text'
                    },
                }
            }
        }
        es.indices.create(index=index_name, body=doc)

        # 构建文档并索引
        for item in data:
            es.index(index=index_name, id=item["id"], body=item)

        # 刷新索引以使更改生效
        es.indices.refresh(index=index_name)

        print("索引构建完成")
```

随后将处理好的`data_pagerank.json`读入到内存中，并且转化为字典。随后检测是否在Elasticsearch中存在与index_name名称相同的索引，如果没有才进行创建。

首先是建立一个合适的doc，在其中选好分词工具以及划分好mapping，随后就使用`es.indices.create(index=index_name, body=doc)`指令进行索引的创建

然后是将`data_pagerank.json`中的数据构建文档并且索引，这里使用了一个简单的for循环遍历整个字典

最后构建完索引就刷新索引以使更改生效



## 查询服务

相关部分在`flask/run.py`中的`search()`, `generate_query()`函数中



当用户进行搜索操作时，`search()`,会判断是否是高级搜索，如果不是就会调用`generate_query()`对搜索的query进行组装，然后调用`es.search(index=index_name, body=query)`调用Elasticsearch进行内容查询

在`generate_query()`中，具体的封装如下

```python
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
```

在`"query": q,`中进行单词的查询，在下列代码中增添全字匹配，如果有全字匹配的结果就优先展示

```python
"bool": {
    "should": [
        {"match_phrase": {"body": q}},
        {"match_phrase": {"title": q}},
        {"match_phrase": {"auth": q}},
    ]
}
```

最后将查询得到的结果进行封装，然后展示到网页上

以下是一个普通搜索得到的例子

<img src="./assets/image-20231227192527818.png" alt="image-20231227192527818" style="zoom:50%;" />

虽然普通搜索的功能能够满足大部分使用需求，但是普通搜索也有局限性。例如搜索文本过长时，会将搜索文本拆分逐个匹配，这样我们不希望看到的结果可能得分会比我们希望看到的结果得分要高

<img src="./assets/image-20231227192732630.png" alt="image-20231227192732630" style="zoom:50%;" />



为了解决这个问题，我们就要引入高级搜索。



## 高级搜索

相关部分在`flask/run.py`中的`search()`, `generate_custom_query()`函数中



高级搜索中我定义了四个功能，分别是**显示搜索高亮**、**包含任意关键词**、**包含完整关键词**、**不要包含关键词**四个功能

<img src="./assets/image-20231227193115331.png" alt="image-20231227193115331" style="zoom: 80%;" />

### 搜索高亮

搜索高亮功能是在query的封装中实现的

```python
"highlight": {
    "pre_tags": ["<strong>"],
    "post_tags": ["</strong>"],
    "fields": {"body": {}, "title": {}, "auth": {}, "appreciation": {}},
},
```

在query封装时加上上面的代码，就会在返回结果中包含一个`highlight`项，其中会对匹配到的搜索关键字进行标注，有了这个就可以实现类似于下面效果的结果高亮

<img src="./assets/image-20231227193516397.png" alt="image-20231227193516397" style="zoom:50%;" />



### 包含任意关键词

在高级搜索栏的`包含任意关键词`一栏中填入数个关键词，并且用`空格`隔开，就可以得到包含有输入的关键词的查询结果

<img src="./assets/image-20231227193641984.png" alt="image-20231227193641984" style="zoom:50%;" />

<img src="./assets/image-20231227193804932.png" alt="image-20231227193804932" style="zoom:50%;" />



具体实现是在query封装时，将分词后的结果进行逐个添加

```python
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
```

其会在query添加一个bool查询，并且设置为should，以及添加短语匹配`match_phrase`



### 包含完整关键词

在高级搜索栏的`包含完整关键词`一栏中填入一个关键词，就可以得到包含有输入的完整关键词的查询结果（如果有匹配项的话）

<img src="./assets/image-20231227201046580.png" alt="image-20231227201046580" style="zoom:50%;" />

同时也可以选择关键词在哪个部分，如果不选择会默认给你选择**内容**部分

<img src="./assets/image-20231227201859411.png" alt="image-20231227201859411" style="zoom: 80%;" />

具体实现是在query封装时，将搜索后的结果进行添加

```python
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
```

其会在query添加一个bool查询，并且设置为must，以及添加短语匹配`match_phrase`



### 不要包含关键词

首先是不进行关键词排除的结果如下

<img src="./assets/image-20231227202047485.png" alt="image-20231227202047485" style="zoom:50%;" />

添加一个不要包含关键词 **莎茵细**，可以看到原本处在首位的搜索结果消失了

<img src="./assets/image-20231227202152378.png" alt="image-20231227202152378" style="zoom:50%;" />



具体实现是在query封装时，将搜索后的结果分词后进行逐个添加

```python
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
```

其会在query添加一个bool查询，并且设置为must_not，以及添加短语匹配`match_phrase`



## 个性化查询

为了实现个性化查询，首先要记录用户的输入历史，我将其存入到一个叫做`user.json`的文件中

```json
"username": {
        "password": "password",
        "history": [
            "西楼落月",
            "花落",
            "鸟",
            "李白",
            "来者可追",
            "知来者之可追"
        ]
    }
```

以下结果分别是没有搜索记录和有搜索记录的结果

<img src="./assets/image-20231227205415349.png" alt="image-20231227205415349" style="zoom:50%;" />

<img src="./assets/image-20231227205359357.png" alt="image-20231227205359357" style="zoom:50%;" />

可以看到它针对用户的搜索历史进行了一个重新排序的过程，能够让用户的每次搜索结果更贴近喜好



具体实现在`re_sort()`函数中进行搜索结果的重排序

```python
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
```

函数首先运行`sort_results`，将搜索历史与搜索结果进行一个相似度匹配，随后根据搜索得分、相似度、pagerank三个量进行不同权重的打分，最后根据这个得分重新排序

计算相似度是在`calculate_similarity`函数中，它先将每个搜索结果的标题、作者、内容连接成一串文本，随后调用`cosine_similarity`函数来计算两段文本之间的余弦相似度。这个相似度计算使用了文本的词频来表示文本的向量形式，通过余弦相似度来衡量两个文本向量之间的相似程度。

最后将重排序的结果返回。



## 个性化推荐

<img src="./assets/image-20231227205710061.png" alt="image-20231227205710061" style="zoom:50%;" />

在网页右侧有一个**猜你喜欢**，是根据用户的搜索历史进行推荐

具体实现是在`recommendation_query`函数中

```python
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
```

简单来说是运用了Elasticsearch的`more_like_this`功能，能够通过填写`like`项在不同的`fields`进行推荐，然后使用`es.search(index=index_name, body=query)`进行推荐查询，最后将得到的结果展示在网页中。
