import sys
import requests

from config import MY_PORT


def requestjson(agent_id: int,user_query_interval_revision: int):
    url = f'http://localhost:{MY_PORT}/check?agent_id={agent_id}&user_query_interval_revision={user_query_interval_revision}'
    try:
        response = requests.get(url)
        print(f"Check agent_id = {agent_id} - {user_query_interval_revision} : {response.status_code}")
        return True

    except requests.RequestException as e:
        print(f"Произошла ошибка при отправке запроса: {e}")
        return False

try:
    requestjson(1,0)
    requestjson(2, 5)
except:
    sys.exit(1)