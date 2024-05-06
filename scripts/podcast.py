import argparse
import json
import os
import pendulum
from retrying import retry
import requests
from notion_helper import NotionHelper
import utils
from dotenv import load_dotenv

load_dotenv()
DOUBAN_API_HOST = os.getenv("DOUBAN_API_HOST", "frodo.douban.com")
DOUBAN_API_KEY = os.getenv("DOUBAN_API_KEY", "0ac44ae016490db2204ce0a042db2916")

from config import (
    movie_properties_type_dict,
    book_properties_type_dict,
    TAG_ICON_URL,
)
from utils import get_icon


headers = {
    "host": "api.xiaoyuzhoufm.com",
    "applicationid": "app.podcast.cosmos",
    "x-jike-refresh-token": os.getenv("REFRESH_TOKEN"),
    "x-jike-device-id": "5070e349-ba04-4c7b-a32e-13eb0fed01e7",
}


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def refresh_token():
    url = "https://api.xiaoyuzhoufm.com/app_auth_tokens.refresh"
    resp = requests.post(url, headers=headers)
    if resp.ok:
        token = resp.json().get("x-jike-access-token")
        headers["x-jike-access-token"] = token


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def get_podcast():
    results = []
    url = "https://api.xiaoyuzhoufm.com/v1/subscription/list"
    data = {
        "limit": 25,
        "sortBy": "subscribedAt",
        "sortOrder": "desc",
    }
    loadMoreKey = ""
    while loadMoreKey is not None:
        if loadMoreKey:
            data["loadMoreKey"] = loadMoreKey
        resp = requests.post(url, json=data, headers=headers)
        if resp.ok:
            loadMoreKey = resp.json().get("loadMoreKey")
            results.extend(resp.json().get("data"))
        else:
            refresh_token()
            raise Exception(f"Error {data} {resp.text}")
    return results


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def get_mileage():
    results = []
    url = "https://api.xiaoyuzhoufm.com/v1/mileage/list"
    data = {"rank": "TOTAL"}
    loadMoreKey = ""
    while loadMoreKey is not None:
        if loadMoreKey:
            data["loadMoreKey"] = loadMoreKey
        resp = requests.post(url, json=data, headers=headers)
        if resp.ok:
            loadMoreKey = resp.json().get("loadMoreKey")
            for item in resp.json().get("data"):
                podcast = item.get("podcast")
                podcast["playedSeconds"] = item.get("playedSeconds", 0)
                results.append(podcast)
        else:
            refresh_token()
            raise Exception(f"Error {data} {resp.text}")
    return results


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def get_episode(pid, timestamp):
    results = []
    url = "https://api.xiaoyuzhoufm.com/v1/episode/list"
    data = {
        "limit": 25,
        "pid": pid,
    }
    loadMoreKey = ""
    while loadMoreKey is not None:
        if loadMoreKey:
            data["loadMoreKey"] = loadMoreKey
        resp = requests.post(url, json=data, headers=headers)
        if resp.ok:
            loadMoreKey = resp.json().get("loadMoreKey")
            d = resp.json().get("data")
            for item in d:
                pubDate = pendulum.parse(item.get("pubDate")).in_tz("UTC").int_timestamp
                if pubDate <= timestamp:
                    return results
                item["pubDate"] = pubDate
                results.append(item)
        else:
            refresh_token()
            raise Exception(f"Error {data} {resp.text}")
    return results


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def get_history():
    results = []
    url = "https://api.xiaoyuzhoufm.com/v1/episode-played/list-history"
    data = {
        "limit": 25,
    }
    loadMoreKey = ""
    while loadMoreKey is not None:
        if loadMoreKey:
            data["loadMoreKey"] = loadMoreKey
        resp = requests.post(url, json=data, headers=headers)
        if resp.ok:
            loadMoreKey = resp.json().get("loadMoreKey")
            d = resp.json().get("data")
            for item in d:
                episode = item.get("episode")
                pubDate = pendulum.parse(episode.get("pubDate")).in_tz("UTC").int_timestamp
                episode["pubDate"] = pubDate
                results.append(episode)
        else:
            refresh_token()
            raise Exception(f"Error {data} {resp.text}")
    return results


def check_podcast(pid):
    """检查是否已经插入过"""
    filter = {"property": "Pid", "rich_text": {"equals": pid}}
    response = notion_helper.query(
        database_id=notion_helper.podcast_database_id, filter=filter
    )
    if len(response["results"]) > 0:
        return response["results"][0].get("id")


def check_eposide(eid):
    """检查是否已经插入过"""
    filter = {"property": "Eid", "rich_text": {"equals": eid}}
    response = notion_helper.query(
        database_id=notion_helper.episode_database_id, filter=filter
    )
    if len(response["results"]) > 0:
        return response["results"][0].get("id")


def get_timestamp(id):
    """检查是否已经插入过"""
    filter = {"property": "Podcast", "relation": {"contains": id}}
    sorts = [
        {
            "property": "时间戳",
            "direction": "descending",
        }
    ]
    response = notion_helper.query(
        database_id=notion_helper.episode_database_id,
        filter=filter,
        sorts=sorts,
        page_size=1,
    )
    if len(response["results"]) > 0:
        return response["results"][0].get("properties").get("时间戳").get("number")
    return 0


def delete():
    """删除未听的"""
    filter = {"property": "状态", "status": {"equals": "未听"}}
    results = notion_helper.query_all(
        database_id=notion_helper.episode_database_id, filter=filter
    )
    for index,result in enumerate(results):
        print(f"正在删除第{index+1}个，共{len(results)}个")
        notion_helper.delete_block(block_id=result.get("id"))


def merge_podcast(list1, list2):
    results = []
    results.extend(list1)
    d = {x.get("pid"): x for x in list1}
    for item in list2:
        if item.get("pid") not in d:
            results.append(item)
    return results


def insert_podcast():
    list1 = get_mileage()
    list2 = get_podcast()
    results = merge_podcast(list1, list2)
    dict = {}
    for index, result in enumerate(results):
        podcast = {}
        podcast["播客"] = result.get("title")
        podcast["Brief"] = result.get("brief")
        pid = result.get("pid")
        podcast["Pid"] = pid
        podcast["收听时长"] = result.get("playedSeconds", 0)
        podcast["Description"] = result.get("description")
        podcast["链接"] = f"https://www.xiaoyuzhoufm.com/podcast/{result.get('pid')}"
        if result.get("latestEpisodePubDate"):
            podcast["最后更新时间"] = (
                pendulum.parse(result.get("latestEpisodePubDate"))
                .in_tz("UTC")
                .int_timestamp
            )
        cover = result.get("image").get("picUrl")
        podcast["全部"] = [
            notion_helper.get_relation_id(
                "全部", notion_helper.all_database_id, TAG_ICON_URL
            )
        ]
        podcast["作者"] = [
            notion_helper.get_relation_id(
                x.get("nickname"),
                notion_helper.author_database_id,
                x.get("avatar").get("picture").get("picUrl"),
            )
            for x in result.get("podcasters")
        ]
        properties = utils.get_properties(podcast, movie_properties_type_dict)
        parent = {
            "database_id": notion_helper.podcast_database_id,
            "type": "database_id",
        }
        print(
            f"正在同步 = {result.get('title')}，共{len(results)}个播客，当前是第{index+1}个"
        )
        
        page_id = check_podcast(pid)
        if page_id:
            notion_helper.update_page(page_id=page_id, properties=properties)
        else:
            page_id = notion_helper.create_page(
                parent=parent, properties=properties, icon=get_icon(cover)
            ).get("id")
        dict[pid] =(page_id, cover)
    return dict


def insert_episode(episodes, d):
    episodes.sort(key=lambda x: x["pubDate"])
    for index, result in enumerate(episodes):
        pid = result.get("pid")
        if pid not in d:
            continue
        episode = {}
        episode["标题"] = result.get("title")
        episode["Description"] = result.get("description")
        episode["时间戳"] = result.get("pubDate")
        episode["发布时间"] = result.get("pubDate")
        episode["音频"] = result.get("media").get("source").get("url")
        eid = result.get("eid")
        episode["Eid"] = eid
 
        episode["时长"] = result.get("duration")
        episode["喜欢"] = result.get("isPicked")
        episode["Podcast"] = [d.get(pid)[0]]
        episode["链接"] = f"hhttps://www.xiaoyuzhoufm.com/episode/{result.get('eid')}"
        status = "未听"
        if result.get("isFinished"):
            status = "听过"
        elif result.get("isPlayed"):
            status = "在听"
        episode["状态"] = status
        properties = utils.get_properties(episode, book_properties_type_dict)
        print(
            f"正在同步 = {result.get('title')}，共{len(episodes)}个Episode，当前是第{index+1}个"
        )
        parent = {
            "database_id": notion_helper.episode_database_id,
            "type": "database_id",
        }
        page_id = check_eposide(eid)
        if page_id:
            notion_helper.update_page(page_id=page_id, properties=properties)
        else:
            notion_helper.create_page(
                parent=parent, properties=properties, icon=get_icon(d.get(pid)[1])
            )


if __name__ == "__main__":
    notion_helper = NotionHelper()
    refresh_token()
    d = insert_podcast()
    episodes = get_history()
    insert_episode(episodes, d)
    delete()
