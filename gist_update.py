import os

import requests
from dotenv import load_dotenv

load_dotenv()
# 必填参数
GIST_ID = os.getenv("GIST_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_gist_content():
    load_dotenv()
    url = f"https://gist.githubusercontent.com/youngqqcn/{GIST_ID}/raw/"
    print(url)
    old_text = requests.get(url).text
    return old_text


def update_gist(content: str):

    # 发送 PATCH 请求更新 Gist
    response = requests.patch(
        f"https://api.github.com/gists/{GIST_ID}",
        headers=HEADERS,
        json={
            "description": "fantopia活动信息收集",
            "files": {"event_info_collection.txt": {"content": content}},
        },
    )

    # 打印结果
    if response.status_code == 200:
        print("Gist 更新成功！")
    else:
        print("更新失败:", response.status_code, response.text)
    pass
