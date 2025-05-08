from playwright.sync_api import sync_playwright

TARGET_API_KEYWORD = "/fanapiWeb/eventsInfo/getEventsInfoPage"  # 根据你的 API 路径关键词调整

captured_request = None  # 保存目标请求

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

    # 提取 headers 并发送相同的请求
    if captured_request:
        headers = captured_request.headers
        post_data = captured_request.post_data
        method = captured_request.method
        url = captured_request.url

        print(f"📨 正在复用请求 {method} {url}")
        response = context.request.fetch(
            url,
            method=method,
            headers=headers,
            data=post_data
        )

        print("🎯 响应状态:", response.status)
        try:
            print("📄 响应数据:", response.json())
        except:
            print("📄 响应文本:", response.text())
    else:
        print("⚠️ 未能捕获 API 请求，请确认关键词或延长等待时间")

    browser.close()
