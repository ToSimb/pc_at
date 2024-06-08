import sys
import json
import requests


def requestjson(final_result, agent_reg_id: str):
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
    url = f'http://localhost:8000/agent-scheme?agent_reg_id={agent_reg_id}'
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=final_result, headers=headers)
        if response.status_code == 200:
            print(f"Регистрация агента {agent_reg_id} успешная.")
            return True
        else:
            print(f"Произошла ошибка: {response.status_code}")
            print(f"Произошла ошибка: {response.text}")
            error_str = str(response.status_code) + " : " + str(response.text)
            raise Exception(error_str)
    except requests.RequestException as e:
        print(f"Произошла ошибка при отправке запроса: {e}")
        return False

def open_json(name_file: str):
    with open(name_file, 'r', encoding='utf-8') as file:
        data = file.read()
    return json.loads(data)

try:
    scheme_agent_1 = open_json("json/AgentScheme(reg_id=1.1.1.3).json")
    requestjson(scheme_agent_1, "1.1.1.3")
except:
    sys.exit(1)