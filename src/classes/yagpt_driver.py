import requests

class YaGPTDriver:

    def __init__(self):

        self.api_key =
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YAGPTSECRET}"
        }

payload = {
    "modelUri": "gpt://b1g9ug9v4e6fnpu7qt5f/yandexgpt/latest",
    "completionOptions": {
        "stream": True,
        "temperature": 0.5,
        "maxTokens": 100
    },
    "messages": [
        {
            "role": "user",
            "text": "Скажи 'все работает'"
        }
    ]
}

# Отправка запроса
response = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
                         headers=headers,
                         json=payload)

if response.status_code == 200:
    response_data = response.json()
    print(response_data["result"]["alternatives"][0]["message"]["text"])
else:
    print("Ошибка при отправке запроса")
    print(response.content)


api_key = "AQVNyRLG1JEK1jUXdnw_WurFQYKO7KcohPFtptHq"
