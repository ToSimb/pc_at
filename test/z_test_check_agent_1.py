import sys
import json
import requests

from config import MY_PORT

def requestjson():
    url = f'http://localhost:{MY_PORT}/check?agent_id=1&user_query_interval_revision=0'
    try:
        response = requests.post(url)

        if response.status_code == 200:
            return response.json()  # или response.text, в зависимости от формата ответа
        else:
            print(f"Ошибка сервера: {response.status_code}")
            return False

    except requests.RequestException as e:
        print(f"Произошла ошибка при отправке запроса: {e}")
        return False
try:
    requestjson()
except:
    sys.exit(1)