import time
import signal
import sys

from database.pf import Pf
from database.sch_ver import Sch_ver
from database.gui import Gui
from database.postgres import connect, disconnect



def signal_handler(sig, frame):
    print("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

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

# vvk_id = None

try:
    while True:
        start_time = time.time()
        params = db_pf.pf_select_params_json(30000)
        result_id, value = parse_value(params)

        vvk_id, scheme_revision, user_query_interval_revision, t3 = db_sch.sch_ver_select_vvk_details()
        t3 = t3 if t3 is not None else 20

        if vvk_id:
            result = {
                "scheme_revision": scheme_revision,
                "user_query_interval_revision": user_query_interval_revision,
                "value": value
            }
            updated_rows = 0
            if result_id != []:
                a = 0 / 0
                updated_rows = db_pf.pf_update_sent_status(result_id)
                db_gui.gui_update_value(vvk_id, None, False)
            end_time = time.time()
            count_sent_false = db_pf.pf_select_count_sent_false()
            print("Время формирование ПФ:", end_time - start_time, "Отправлено:", updated_rows, "Осталост строк не отправленных:", count_sent_false)
            if count_sent_false > 30000:
                t3 = 0
        else:
            print("Нет зарегестрированного ВВК")
        end_time = time.time()

        time.sleep(t3)


except Exception as e:
    error_str = str(e)
    if vvk_id:
        db_gui.gui_update_value(vvk_id, error_str, False)
    print("Произошла ошибка: %s", error_str)
    disconnect(conn)
    sys.exit(1)