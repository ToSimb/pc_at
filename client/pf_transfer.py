import requests
import datetime
import time
import signal
import sys

from database.pf import Pf
from database.sch_ver import Sch_ver
from database.gui import Gui
from database.postgres import connect, disconnect
from logger.logger import logger
from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT

INT_LIMIT = 30000
T3 = 20

def signal_handler(sig, frame):
    logger.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

def request_json(final_result, vvk_id):
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
            error_str = "Произошла ошибка при отправке данных:" + str(response.status_code) + " : " + str(response.text)
            raise Exception(error_str)
    except requests.RequestException as e:
        logger.error(f"Произошла ошибка при отправке данных: {e}")
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
db_gui = Gui(conn)
db_pf = Pf(conn)
db_sch = Sch_ver(conn)

vvk_id = None # Необходима для исколючения

try:
    while True:
        start_time = time.time()

        params = db_pf.pf_select_params_json(INT_LIMIT)
        result_id, value = parse_value(params)
        vvk_id, scheme_revision, user_query_interval_revision, t3 = db_sch.sch_ver_select_vvk_details()
        t3 = t3 if t3 is not None else T3
        if result_id != []:
            if vvk_id:
                result = {
                    "scheme_revision": scheme_revision,
                    "user_query_interval_revision": user_query_interval_revision,
                    "value": value
                }
                start_request_time = time.time()
                if request_json(result, vvk_id):
                    updated_rows = db_pf.pf_update_sent_status(result_id)
                    db_gui.gui_update_value(vvk_id, None, False)
                    count_sent_false = db_pf.pf_select_count_sent_false()
                    logger.info("DB(pf): изменено строк (true): %d | ОСТАЛОСЬ в БД: %d", updated_rows, count_sent_false)
                    if count_sent_false > INT_LIMIT:
                        t3 = 0
                end_request_time = time.time()
                logger.info("Время формирование ПФ: %.4f | время отправки: %.4f", start_request_time-start_time, end_request_time-start_request_time)
            else:
                logger.info("Нет зарегестрированного ВВК")
        else:
            logger.info("В БД нет новых данных")

        end_time = time.time()
        time_transfer = end_time - start_time
        time_transfer = t3 if time_transfer > t3 else time_transfer

        time.sleep(t3 - time_transfer)

except Exception as e:
    error_str = str(e)
    if vvk_id:
        db_gui.gui_update_value(vvk_id, error_str, False)
    logger.error("Произошла ошибка: %s", error_str)
    disconnect(conn)
    sys.exit(1)