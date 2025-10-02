import os
import re
import json
import logging

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

OPENAI_API_KEY = os.getenv("AI_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.proxyapi.ru/openai/v1")

async def generate_text(prompt, model="gpt-4o-mini"):
    response = client.responses.create(
        model=model,
        input=prompt,
    )
    return response.output_text

async def get_json_as_map(prompt, model="gpt-4o-mini") -> dict:
    response = await generate_text(prompt, model)

    try:
        match = re.search(r"```json\n(.+?)\n```", response, re.DOTALL)

        if match:
            json_str = match.group(1)
            return json.loads(json_str)
    except:
        logging.error("Cannot parse json from ProxyAPI")