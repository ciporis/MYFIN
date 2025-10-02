import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("AI_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.proxyapi.ru/openai/v1")

async def convert_voice_to_text(voice_path: str):
    with open(voice_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            prompt="Этот аудио файл должен содеражть данные о команде, которую должен выполнить телеграм бот."
        )

        print(transcription)

        return transcription
