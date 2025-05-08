import os

from dotenv import load_dotenv
from openai import OpenAI


def call_deepseek(message_text: str) -> str:
    load_dotenv()

    system_prompts = open("prompts.txt", "r", encoding="utf-8").read()

    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompts},
            {"role": "user", "content": message_text},
        ],
        stream=False,
    )

    output = response.choices[0].message.content
    print(output)
    return output
