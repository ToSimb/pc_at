import sys
import os
import signal
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client.database.postgres import connect, disconnect
from client.database.db import Database


def signal_handler(sig, frame):
    print("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

TIME3 = 1
TEMPLATES_ID = "agent_connection"
METRIC_ID = "connection.agent"

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

conn = connect()
db = Database(conn)

time_counter = 1

def time_change(ans):
    if ans is None:
        return 0
    timestamp_float = ans.timestamp()
    timestamp_int = int(timestamp_float)
    return timestamp_int

try:
    while True:
        time_counter += 1
        start_time = time.time()
        print("_____________")
        print(int(start_time))
        if db.sch_ver_select_latest_status():
            value = []
            len_pf = 0
            dump = db.gui_select_agents_details()
            for item in dump:
                # Проверка, что агент зарегистрирован
                result = None
                if item[0] is not None:
                    print(f"Agent {item[0]}")
                    late_time = max(time_change(item[1]), time_change(item[2]))
                    # Проверка, что было выполнялось хоть раз params/check
                    if late_time > 0:
                        print(late_time)
                        status = True
                        # если не было ответа от агента больше 5 секунд - ERROR
                        if int(start_time) - late_time > 5:
                            status = False
                            db.gui_update_check_number_id_false(item[0])
                        query_interval_all = db.reg_sch_get_query_intervals(item[0], METRIC_ID)
                        item_ids = db.reg_sch_get_item_ids(item[0], TEMPLATES_ID)
                        # проверка, что есть пути с контролем связи
                        if item_ids is not None:
                            for item_id in item_ids:
                                print(f" Item_id {item_id}")
                                # проверка, что метрика для контроля связи есть
                                if query_interval_all is not None:
                                    if time_counter % query_interval_all == 0:
                                        result = {
                                            'item_id': item_id,
                                            'metric_id': METRIC_ID,
                                        }
                                        if status:
                                            data_item = {
                                                't': int(start_time),
                                                'v': "OK"
                                            }
                                        else:
                                            comment_error = f"Нет связи с Агентом: {item[0]}"
                                            data_item = {
                                                't': int(start_time),
                                                'v': "ERROR",
                                                'comment': comment_error
                                            }
                                        result.update(data_item)
                                        len_pf += 1
                if result is not None:
                    value.append(result)
            print(value)
            if len_pf > 0:
                db.pf_insert_params_of_1_packet(0, len_pf, value)

        end_time = time.time()
        total_time = end_time - start_time
        adjusted_total_time = min(total_time, TIME3)
        print(f"Time {adjusted_total_time}")
        time.sleep(TIME3 - adjusted_total_time)

except Exception as e:
    disconnect(conn)
    print(e)