import networkx as nx
import requests
import time
import json
import os
import re
import retry
from retry.api import retry_call
from bs4 import BeautifulSoup
from tqdm import tqdm


def spider_index():
    def process_page(url, type, num_pages):
        data_list = []
        error_pages = []
        with tqdm(total=num_pages, desc=f"Processing {type} pages") as pbar:
            for page in range(num_pages):
                page_url = url + str(page)
                try:
                    time.sleep(1.5)
                    response = requests.get(page_url)
                    if response.status_code == 200:
                        json_data = response.json()
                        items = json_data.get("list", [])

                        for item in items:
                            data = {
                                "id": item["id"],
                                "url": f"https://www.gushici.com/t_{item['id']}",
                                "title": item["title"],
                                "auth": item["auth"],
                                "auth_id": item["auth_id"],
                                "auth_intro": item["intro"],
                                "dynasty": item["dynasty"],
                                "type": type,
                                "body": re.sub("<span.*?>.*?</span>", "", item["body"]),
                                "translation": item["translation"],
                                "explanation": item["explanation"],
                                "appreciation": item["appreciation"],
                                "related": retry_call(
                                    spider_link,
                                    fargs=[f"https://www.gushici.com/t_{item['id']}"],
                                ),
                            }
                            data_list.append(data)
                    else:
                        print("\nprocess_page", response.status_code, " url:", page_url)
                        error_pages.append(page)
                except Exception as e:
                    print("Error occurred on page:", page)
                    print("Error message:", str(e))
                    error_pages.append(page)

                pbar.update(1)

        # 重新爬取出错的页面
        for page in error_pages:
            page_url = url + str(page)
            try:
                response = requests.get(page_url)
                if response.status_code == 200:
                    json_data = response.json()
                    items = json_data.get("list", [])

                    for item in items:
                        data = {
                            "id": item["id"],
                            "url": f"https://www.gushici.com/t_{item['id']}",
                            "title": item["title"],
                            "auth": item["auth"],
                            "auth_id": item["auth_id"],
                            "auth_intro": item["intro"],
                            "dynasty": item["dynasty"],
                            "type": type,
                            "body": re.sub(
                                "<span.*?>.*?</span>", "", item["body"]
                            ),  # 主体
                            "translation": item["translation"],  # 翻译
                            "explanation": item["explanation"],  # 注释
                            "appreciation": item["appreciation"],  # 赏析
                            "related": retry_call(
                                spider_link,
                                fargs=[f"https://www.gushici.com/t_{item['id']}"],
                            ),
                        }
                        data_list.append(data)
                else:
                    print("\nprocess_page", response.status_code, " url:", page_url)
                    time.sleep(30)
            except Exception as e:
                print("\nError occurred on page:", page)
                print("Error message:", str(e), "\n")
                time.sleep(30)
        return data_list

    url_shi = "https://www.gushici.com/poetry_list?type=诗&page="
    url_ci = "https://www.gushici.com/poetry_list?type=词&page="
    url_qu = "https://www.gushici.com/poetry_list?type=曲&page="
    url_wenyanwen = "https://www.gushici.com/poetry_list?type=文言文&page="

    data_list = []

    data_list.extend(process_page(url_shi, "诗", 1097))
    data_list.extend(process_page(url_ci, "词", 793))
    data_list.extend(process_page(url_qu, "曲", 144))
    data_list.extend(process_page(url_wenyanwen, "文言文", 50))

    file_path = os.path.join(
        os.path.join(os.path.dirname(os.path.abspath(__file__))),
        "data1.json",
    )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data_list, file, ensure_ascii=False, indent=4)


@retry.retry(tries=3, delay=10)
def spider_link(url):
    response = requests.get(url)
    time.sleep(1)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", class_="poem-title")
        href_list = []
        for link in links:
            href = link.get("href")
            href_list.append("https://www.gushici.com" + href)
        return href_list
    else:
        print("\nspider_link", response.status_code, " url:", url)


def add_pagerank(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data_list = json.load(file)

    G = nx.DiGraph()
    for item in data_list:
        mainlink = item["url"]
        related_links = item.get("related")  # 使用get方法获取related字段，避免NoneType错误
        G.add_node(mainlink)
        if related_links is not None:  # 检查related_links是否为None
            for link in related_links:
                G.add_edge(mainlink, link)

    pageranks = nx.pagerank(G)

    for item in data_list:
        url = item["url"]
        item["pagerank"] = pageranks[url]

    with open("data_pagerank.json", "w", encoding="utf-8") as file:
        json.dump(data_list, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    if os.path.exists("data1.json"):
        pass
    else:
        spider_index()
        print("初次爬取成功")

    add_pagerank("data1.json")
