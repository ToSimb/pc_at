import sys
import time
import random
import requests

from config import MY_PORT

def requestjson(url, final_result):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=final_result, headers=headers)
        if response.status_code == 200:
            print("Данные успешно отправлены.")
            return True
        elif response.status_code == 227:
            print("Данные отправлены, но ошибка 227")
            return True
        else:
            print(f"Произошла ошибка: {response.status_code}")
            print(f"Произошла ошибка: {response.text}")
            error_str = str(response.status_code) + " : " + str(response.text)
            raise Exception(error_str)
    except requests.RequestException as e:
        print(f"Произошла ошибка при отправке запроса: {e}")
        return False

def if_int():
    data = []
    metric_data = {"t": current_timestamp - 2, "v": str(random.randint(800, 1100))}
    data.append(metric_data)
    # metric_data = {"t": current_timestamp - 2, "v": str()}
    # data.append(metric_data)
    metric_data = {"t": current_timestamp - 1, "v": str(random.randint(800, 1100)), "etmax": False, "etmin": True,
                   "comment": "Test"}
    data.append(metric_data)
    metric_data = {"t": current_timestamp, "v": str(random.randint(800, 1100)), "etmin": True, "comment": "Арбуз"}
    data.append(metric_data)
    return data

def if_double():
    data = []
    metric_data = {"t": current_timestamp - 2, "v": str(random.uniform(800, 1100))}
    data.append(metric_data)
    metric_data = {"t": current_timestamp - 1, "v": str(random.uniform(800, 1100)), "etmax": False, "etmin": True,
                   "comment": "Test"}
    data.append(metric_data)
    metric_data = {"t": current_timestamp, "v": str(random.uniform(800, 1100)), "etmin": True, "comment": "Арбуз"}
    data.append(metric_data)
    return data

def if_state():
    data = []
    metric_data = {"t": current_timestamp - 2, "v": "OK"}
    data.append(metric_data)
    metric_data = {"t": current_timestamp - 1, "v": "FATAL", "etmax": False, "etmin": True,
                   "comment": "Test"}
    data.append(metric_data)
    metric_data = {"t": current_timestamp, "v": "ERROR", "etmin": True, "comment": "Арбуз"}
    data.append(metric_data)
    return data

def if_str():
    data = []
    metric_data = {"t": current_timestamp - 1, "v": "FAasdasTAL", "etmax": False, "etmin": True,
                   "comment": "Test"}
    data.append(metric_data)
    return data

try:
    final_result = {
        "scheme_revision": 0,
        "user_query_interval_revision": 1,
        "value": []
    }
    # for _ in range(random.randint(1,200)):
    for _ in range(100):
        current_timestamp = int(time.time())
        for item_id in range(13, 18):

            for metric_id in ['chassis.uptime',
                              'cpu.user.time',
                              'cpu.core.load',
                              'chassis.memory.total',
                              'chassis.memory.used',
                              'сompboard.voltage',
                              'сompboard.power',
                              'сompboard.state']:
                data = []
                if metric_id == 'chassis.uptime':
                    data = if_double()
                if metric_id == 'cpu.user.time':
                    data = if_double()
                if metric_id == 'cpu.core.load':
                    data = if_double()
                if metric_id == 'chassis.memory.total':
                    data = if_int()
                if metric_id == 'chassis.memory.used':
                    data = if_int()
                if metric_id == 'сompboard.voltage':
                    data = if_double()
                if metric_id == 'сompboard.power':
                    data = if_double()
                if metric_id == 'сompboard.state':
                    data = if_state()
                final_result["value"].append({"item_id": item_id, "metric_id": metric_id, "data": data})
    start_time = time.time()
    # random_agent = random.randint(1,2)
    random_agent = 1
    url = f'http://localhost:{MY_PORT}/params?agent_id={random_agent}'
    requestjson(url, final_result)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время отправки и сохранения в БД рандомного агента {random_agent}: {execution_time}")


except Exception as e:
    sys.exit(1)