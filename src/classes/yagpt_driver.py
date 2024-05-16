import json

import requests
from loguru import logger

class YaGPTDriver:

    def __init__(self, api_key=""):

        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {api_key}"
        }

    def query(self, prompt):

        url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
        payload = {
            "modelUri": "gpt://b1g9ug9v4e6fnpu7qt5f/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": 400
            },
            "messages": [
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }

        logger.info("Отправляем запрос Yandex GPT")

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            logger.info("Получен успешно ответ от Yandex GPT")
            logger.info(response.content)

            file = open("temp.json", "w")
            file.write(response.text)
            file.close()

            response_data = json.loads(response.text.strip())

            return response_data["result"]["alternatives"][0]["message"]["text"]
        else:
            logger.error(f"Ошибка при отправке запроса {prompt}")
            logger.error(response.content)
            return response.content

#
# driver = YaGPTDriver(api_key=os.environ.get("YANDEX_API_KEY"))
#
# driver.query("Напиши 'Привет'")
