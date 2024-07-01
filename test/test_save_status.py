import sys
import requests

def requestjson():
    url = f'http://localhost:8000/gui/status_save'
    try:
        response = requests.get(url)
        print("Статус обновлен для сохранения последнего пакета")
        return True

    except requests.RequestException as e:
        print(f"Произошла ошибка при отправке запроса: {e}")
        return False

try:
    requestjson()
except:
    sys.exit(1)