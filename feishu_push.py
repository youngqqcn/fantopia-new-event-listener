# https://open.feishu.cn/api-explorer/cli_a7aa2e266731500b?apiName=patch&from=op_doc_tab&project=docx&resource=document.block&version=v1

# https://open.feishu.cn/api-explorer/cli_a7aa2e266731500b?apiName=patch&from=op_doc_tab&project=docx&resource=document.block&version=v1

import os

import lark_oapi as lark
import requests
from dotenv import load_dotenv
from lark_oapi.api.docx.v1 import *

load_dotenv()

app_id = os.getenv("APP_ID")
app_secret = os.getenv("APP_SECRET")


def get_tenant_access_token():
    # 使用 user_access_token 需开启 token 配置, 并在 request_option 中配置 token
    client = (
        lark.Client.builder()
        .enable_set_token(True)
        .app_secret(app_secret)
        .app_id(app_id)
        .log_level(lark.LogLevel.DEBUG)
        .build()
    )

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    # 应用凭证里的 app id 和 app secret
    post_data = {
        "app_id": app_id,
        "app_secret": app_secret,
    }
    r = requests.post(url, data=post_data)
    tat = r.json()["tenant_access_token"]
    print("tat: ", tat)


def main():
    # 创建client
    print()
    client = (
        lark.Client.builder()
        .app_id(os.getenv("APP_ID"))
        .app_secret(os.getenv("APP_SECRET"))
        .log_level(lark.LogLevel.DEBUG)
        .build()
    )

    # 构造请求对象
    request: GetDocumentRequest = (
        GetDocumentRequest.builder().document_id("L1O3dvg8foCF6bx8m2nchXvOnkc").build()
    )

    # 发起请求
    response: GetDocumentResponse = client.docx.v1.document.get(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.docx.v1.document.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
        return

    # client.docx.v1.document_block_children.create({
    #     # "document_revision_id": response.data.document_revision_id,
    #     # "client_token": response.data.client_token,
    #     "user_id_type": "open_id",
    #     "document_id":response.data.document.document_id,
    #     "block_id": response.data.document.revision_id,
    #     "request_body": {
    #         "children": [
    #             {
    #                 "type": "text",
    #                 "text": {
    #                     "content": "Hello, World!"
    #                 }
    #             }
    #         ]
    #     }
    # })

    request: ListDocumentBlockRequest = (
        ListDocumentBlockRequest.builder()
        .document_id("L1O3dvg8foCF6bx8m2nchXvOnkc")
        .page_size(500)
        .document_revision_id(-1)
        .user_id_type("user_id")
        .build()
    )
    response: ListDocumentBlockResponse = client.docx.v1.document_block.list(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.docx.v1.document_block.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
        return
    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    # 构造请求对象
    request: PatchDocumentBlockRequest = (
        PatchDocumentBlockRequest.builder()
        .document_id("L1O3dvg8foCF6bx8m2nchXvOnkc")
        .block_id("MIbrdxsL5occeYxBBJWcmDVwnNh")
        .document_revision_id(-1)
        .user_id_type("user_id")
        .request_body(
            UpdateBlockRequest.builder().update_text(
                UpdateTextRequest.builder()
                .elements(
                    [
                        TextElement.builder()
                        .text_run(
                            TextRun.builder()
                            .content("Hello, World!")
                            .text_element_style(
                                TextElementStyle.builder().text_color("red").build()
                            )
                            .build()
                        )
                        .build()
                    ]
                )
                .fields([1])
                .build()
            )
        )
        .build()
    )
    # 发起请求
    response: PatchDocumentBlockResponse = client.docx.v1.document_block.patch(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.docx.v1.document_block.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    # 处理业务结果
    # lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    load_dotenv()
    main()
