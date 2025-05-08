import datetime
import json
import os
import re

import html2text
from playwright.sync_api import sync_playwright

from deepseek import call_deepseek
from gist_update import get_gist_content, update_gist

TARGET_API_KEYWORD = (
    "/fanapiWeb/eventsInfo/getEventsInfoPage"  # 根据你的 API 路径关键词调整
)

# 初始化 HTML 转 Markdown 转换器
converter = html2text.HTML2Text()
converter.ignore_links = True  # 保留链接
converter.ignore_images = True  # 保留图片
converter.body_width = 0  # 不自动换行

captured_request = None  # 保存目标请求


def get_event_key():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def handle_request(route, request):
            global captured_request
            if TARGET_API_KEYWORD in request.url and not captured_request:
                print(f"✅ 捕获 API 请求: {request.url}")
                captured_request = request
            route.continue_()

        context.route("**/*", handle_request)
        page.goto("https://fantopia.io")
        page.wait_for_timeout(5000)  # 等待页面加载和请求发送

        global captured_request
        # 提取 headers 并发送相同的请求
        if captured_request:
            headers = captured_request.headers
            post_data = captured_request.post_data
            method = captured_request.method
            url = captured_request.url

            print(f"📨 正在复用请求 {method} {url}")
            response = context.request.fetch(
                url, method=method, headers=headers, data=post_data
            )

            print("🎯 响应状态:", response.status)
            # try:
            #     print("📄 响应数据:", response.json())
            # except:
            #     print("📄 响应文本:", response.text())
            print("=========")
            print(json.dumps(response.json(), indent=4))
            open("response.json", "w").write(
                json.dumps(response.json(), indent=4, ensure_ascii=False)
            )

            captured_request = None

            # 遍历所有活动，获取活动详情
            # captured_request = None
            def handle_request2(route, request):
                global captured_request
                tmp_api_keyword1 = "fanapiWeb/eventsInfo/getEventsInfoByEventsKey"
                if tmp_api_keyword1 in request.url and not captured_request:
                    print(f"✅ 捕获 API 请求: {request.url}")
                    captured_request = request
                route.continue_()

            for event in response.json()["data"]["records"]:
                print("活动 key:", event["eventsKey"])
                event_key = str(event["eventsKey"]).strip()
                if os.path.exists(f"events/{event_key}.json") and os.path.exists(
                    f"events/{event_key}.md"
                ):
                    print("⚠️ 已存在文件，跳过")
                    continue
                context.route("**/*", handle_request2)
                page.goto(
                    f"https://www.fantopia.io/events-tickets?eventsKey={event_key}&areaKey=TU8="
                )
                page.wait_for_timeout(3000)
                if captured_request:
                    headers = captured_request.headers
                    post_data = captured_request.post_data
                    method = captured_request.method
                    url = captured_request.url

                    print(f"📨 正在复用请求 {method} {url}")
                    tmp_response = context.request.fetch(
                        url, method=method, headers=headers, data=post_data
                    )

                    print("🎯 响应状态:", tmp_response.status)

                    print("=========")
                    open(f"events/{event['eventsKey']}.json", "w").write(
                        json.dumps(tmp_response.json(), indent=4, ensure_ascii=False)
                    )
                    captured_request = None

                    html_description = tmp_response.json()["data"]["description"]

                    markdown = converter.handle(html_description)
                    # open(f"events/{event['eventsKey']}.md", "w").write(markdown)

                    # 将时间戳转换为可读格式 YYYY-MM-DD HH:MM:SS
                    time_stamp = int(event["sellTimeStamp"])
                    time_stamp = time_stamp / 1000
                    time_stamp = datetime.datetime.fromtimestamp(time_stamp)
                    time_stamp = time_stamp.strftime("%Y-%m-%d %H:%M:%S")

                    event_info = {
                        "title": event["title"],  # 活动标题
                        "eventsKey": event["eventsKey"],  # 活动key
                        "type": event[
                            "type"
                        ],  # 1- 音乐节门票  2-演唱会门票 3-签售会 4-只卖周边
                        "description": markdown,  # 活动描述
                        "startTime": event["startTime"],  # 活动开始时间
                        "endTime": event["endTime"],  # 活动结束时间
                        "sellStartTime": time_stamp,  # 售卖开始时间
                        "limitCount": event["limitCount"],  # 限购数量
                        "symbol": event["symbol"],  # 货币符号
                        "location": event["location"],  # 活动地点
                        # "minPrice": event["minPrice"],  # 最低票价
                        # "maxPrice": event["maxPrice"],  # 最高票价
                        # "ticketSimpleInfoVos": if '' event["ticketSimpleInfoVos"],  # 票种信息
                        # "platforms": event["platforms"],  # 售卖平台
                    }

                    ticket_info = ""
                    if "ticketSimpleInfoVos" in event:
                        for ticket in event["ticketSimpleInfoVos"]:
                            ticket_info += f"{ticket["title"]}  {ticket["symbol"]} {ticket["price"]/100} \n"

                    append_info = f"""
                    **演出活动名称：**: {event_info['title']}
                    **演出活动链接：**: https://www.fantopia.io/events-tickets?eventsKey={event_info['eventsKey']}
                    **活动类型**: {event_info['type']} # 1:音乐节门票  2:演唱会门票 3:签售会 4:周边商品
                    **演出活动开始时间：**: {event_info['startTime']}
                    **活动结束时间**: {event_info['endTime']}
                    **门票公开售票时间**: {event_info['sellStartTime']}
                    **限购数量**: {event_info['limitCount']}
                    **货币符号**: {event_info['symbol']}
                    **演出活动地点：**: {event_info['location']}
                    **票种信息**: {ticket_info}
                    """
                    if "memberSellStartTime" in event and event["memberSellStartTime"]:
                        append_info += (
                            f"**会员购优先购开始时间**: {event['memberSellStartTime']}"
                        )

                    text_for_deepseek = append_info + markdown
                    text_output = call_deepseek(message_text=text_for_deepseek)
                    text_output = text_output.replace("```markdown", "").replace(
                        "```", ""
                    )
                    open(f"events/{event['eventsKey']}.md", "w").write(text_output)
                else:
                    print("⚠️ 未能捕获 API 请求，请确认关键词或延长等待时间")

        else:
            print("⚠️ 未能捕获 API 请求，请确认关键词或延长等待时间")
        browser.close()


def update_event_info_gist():
    old_content = get_gist_content()
    print("old_content:", old_content)
    # 用正则匹配 eventsKey=xxx

    pattern = r"eventsKey=(\w+)&?"
    matches = re.findall(pattern, old_content)
    print("matches:", matches)

    # 遍历events文件夹，读取所有md文件
    update_content = old_content
    for file in os.listdir("events"):
        event_key = os.path.basename(file).removesuffix(".md")
        if event_key in matches:
            print("文件已存在，跳过")
            continue
        if file.endswith(".md"):
            with open(os.path.join("events", file), "r", encoding="utf-8") as f:
                content = f.read()
                content = content.replace("```markdown", "").replace("```", "")
                update_content += (
                    "\n\n====================================\n\n" + content + "\n"
                )

    if update_content != old_content:
        print("内容已更新，准备发送到Gist")
        update_gist(update_content)


if __name__ == "__main__":
    get_event_key()
    update_event_info_gist()
