from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
     # 打开主页
    page.goto("https://www.fantopia.io/")

     # 等待卡片加载完成
    page.wait_for_selector(
        "div.overflow-hidden.font-sans.cursor-pointer.rounded-xl.bg-dark2.select-none"
    )

    #  选中并点击第一个卡片
    cards = page.locator(
        "div.overflow-hidden.font-sans.cursor-pointer.rounded-xl.bg-dark2.select-none"
    )
    cards.nth(0).click()
    # print("8888888888")
    # print(page.content())

    page.wait_for_load_state("networkidle")

    # 获取活动名
    selector = (
         "div.p-6.text-base.text-white "
        "div.w-full"
        # "div.text-center.text-base.text-[#F3F3F3]"
    )
    page.wait_for_selector(selector)
    event_name = page.locator(selector).inner_text()
    print(f"活动名：{event_name}")
    print("=====================")
    print("活动详情：")


    # 获取活动详情
    page.wait_for_selector("div.p-6.text-base.text-white  div.inner-html")
    detail_content = page.locator("div.p-6.text-base.text-white  div.inner-html").inner_text()
    print(detail_content)