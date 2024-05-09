import requests
import datetime
import time
import signal
import sys

from database.pf import Pf
from database.postgres import connect, disconnect
from logger.logger import logger
from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT

def signal_handler(sig, frame):
    logger.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

def requestjson(final_result, vvk_id):
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
    url = f'http://localhost:8000/params?agent_id={vvk_id}'
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=final_result, headers=headers)
        if response.status_code == 200:
            logger.info("Данные успешно отправлены.")
            return True
        elif response.status_code == 227:
            logger.info("Данные отправлены, но ошибка 227")
            return True
        else:
            logger.error(f"Произошла ошибка: {response.status_code}")
            logger.error(f"Произошла ошибка: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Произошла ошибка при отправке запроса: {e}")
        return False

def parse_value(params):
    result = {}
    result_id =[]
    for item in params:
        result_id.append(item['id'])
        item_id = item['item_id']
        metric_id = item['metric_id']
        t = item['t']
        v = item['v']
        comment = item.get('comment')
        etmax = item.get('etmax')
        etmin = item.get('etmin')

        if (item_id, metric_id) not in result:
            result[(item_id, metric_id)] = {
                'item_id': item_id,
                'metric_id': metric_id,
                'data': []
            }

        data_item = {
            't': t,
            'v': v
        }
        if comment is not None:
            data_item['comment'] = comment
        if etmax is not None:
            data_item['etmax'] = etmax
        if etmin is not None:
            data_item['etmin'] = etmin

        result[(item_id, metric_id)]['data'].append(data_item)

    output_data = sorted(result.values(), key=lambda x: (x['item_id'], x['metric_id']))

    return result_id, output_data

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

conn = connect()
db_pf = Pf(conn)

try:
    while True:
        start_time = time.time()
        params = db_pf.pf_select_params_json(20000)
        result_id, value = parse_value(params)

        result = {
            "vvk_id": 0,
            "scheme_revision": 0,
            "user_query_interval_revision": 0,
            "value": value
        }
        point1_time = time.time()
        if requestjson(result, 0):
            updated_rows = db_pf.pf_update_sent_status(result_id)
            logger.info("DB(pf): изменено строк (true): %d | ОСТАЛОСЬ в БД: %d", updated_rows, db_pf.pf_count_cent_false())
        end_time = time.time()
        logger.info("Время формирование ПФ: %.4f | время отправки: %.4f", point1_time-start_time, end_time-point1_time )
        print(end_time-start_time)
        time.sleep(10 - (end_time-start_time))


except Exception as e:
    logger.error("Произошла ошибка: %s", e)
    disconnect(conn)
    sys.exit(1)