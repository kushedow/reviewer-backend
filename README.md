# Сервис skypro-reviewer-backend

## Краткое описание

Сервер для экспериментального плагина по проверке домашек. 
Стек: Python, Fastapi

## Запуск

1 Складываем ключи от сервис-аккаунта гугла на сервер (credentials.json)

2 Задаем переменные окружения

- OPENAI_API_KEY - токен для chat gpt
- CREDENTIALS_PATH - путь к ключами от сервис-аккаунта
- FRONTEND_MIN_VERSION - мин версия фронтенда. Не должна быть больше версии плагина

3 Запускаем

uvicorn main:app --host 0.0.0.0 --port 80 


## Ответственные:

- Code owner: gleb.homutov
- Product owner: vladimir.bayandin, tatiana.lnsk, a.moiseeva
- Команда: Skypro
