import sys
import time
import random
import requests


def requestjson(final_result, vvk_id):
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
    url = f'http://localhost:8000/params?agent_id={vvk_id}'
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


try:
    while True:
        current_timestamp = int(time.time())
        final_result = {
            "scheme_revision": 0,
            "user_query_interval_revision": 0,
            "value": []
        }
        for item_id in range(1, 1000):
            for metric_id in ['chassis.uptime',
                              'cpu.user.time',
                              'cpu.core.load',
                              'chassis.memory.total',
                              'chassis.memory.used',
                              'сompboard.voltage',
                              'сompboard.power',
                              'сompboard.state']:

                data = []
                metric_data = {"t": current_timestamp-10, "v": str(random.randint(800, 1100))}
                data.append(metric_data)
                metric_data = {"t": current_timestamp, "v": str(random.randint(800, 1100)), "comment": "Test"}
                data.append(metric_data)
                metric_data = {"t": current_timestamp+2, "v": str(random.randint(800, 1100)), "etmax": True, "etmin": False}
                data.append(metric_data)
                final_result["value"].append({"item_id": item_id, "metric_id": metric_id, "data": data})
        start_time = time.time()
        requestjson(final_result, 1)
        end_time = time.time()
        execution_time = end_time - start_time
        print("Время отправки и сохранения в БД:", execution_time)

        time.sleep(1)

except Exception as e:
    sys.exit(1)