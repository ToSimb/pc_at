import requests
import datetime
import time
import signal
import sys

from database.pf import Pf
from database.sch_ver import Sch_ver
from database.reg_sch import Reg_sch
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

def request_pf(final_result: dict, vvk_id: int) -> bool:
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
    url = f'http://localhost:8000/params/hole?vvk_id={vvk_id}'
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

def parse_value(params: list) -> tuple:
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

def request_registration_vvk(url: str, json_vvk_return: dict):
    headers = {'Content-Type': 'application/json'}
    try:
        logger.info(f"Отправка: {url}")
        response = requests.post(url, json=json_vvk_return, headers=headers)
        if response.status_code == 200:
            logger.info("Успушная регистрация VvkScheme на стороне АФ")
            return response.json()
        else:
            error_str = "Произошла ошибка при регистрации: " + str(response.status_code) + " : " + str(response.text)
            logger.error(error_str)
            db_gui.gui_update_vvk_reg_error(False, error_str)
            return None
    except requests.RequestException as e:
        error_str = f"RequestException: {e}."
        logger.error(error_str)
        db_gui.gui_update_vvk_reg_error(False, error_str)
        return None


def forming_registration_vvk() -> bool:
    # REG_SCH
    if db_reg.reg_sch_block_check():
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.info(error_str)
        db_gui.gui_update_vvk_reg_error(False, error_str)
        return False
    db_reg.reg_sch_block_true()
    scheme_revision, scheme, metric_info_list = db_reg.reg_sch_select_vvk_scheme()
    data = {
        "scheme_revision": scheme_revision,
        "scheme": scheme
    }
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/vvk-scheme'
    url = f'http://127.0.0.1:8000/agent-scheme/save'
    temp = request_registration_vvk(url, data)
    if temp:
        # GUI
        db_gui.gui_update_vvk_reg(temp["vvk_id"], temp["scheme_revision"], temp["user_query_interval_revision"], True)

        # SCH_VER
        db_sch.sch_ver_insert_vvk(True, temp, scheme, metric_info_list)

        # REG_SCH
        db_reg.reg_sch_update_vvk_id(temp["vvk_id"])
        db_reg.reg_sch_update_all_user_query_revision(temp["user_query_interval_revision"])

        db_reg.reg_sch_block_false()
        return True
    else:
        db_reg.reg_sch_block_false()
        return False

def forming_re_registration_vvk() -> bool:
    # REG_SCH
    if db_reg.reg_sch_block_check():
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.info(error_str)
        db_gui.gui_update_vvk_reg_error(False, error_str)
        return False
    db_reg.reg_sch_block_true()

    vvk_id, scheme_revision, scheme, metric_info_list = db_sch.sch_ver_select_vvk_details_unreg()

    data = {
        "scheme_revision": scheme_revision,
        "scheme": scheme
    }
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/vvk-scheme?vvk_id={vvk_id}'
    url = f'http://127.0.0.1:8000/agent-scheme/save?vvk_id={vvk_id}'
    temp = request_registration_vvk(url, data)
    if temp:
        # GUI
        db_gui.gui_update_vvk_reg(temp["vvk_id"], temp["scheme_revision"], temp["user_query_interval_revision"], True)

        # SCH_VER
        db_sch.sch_ver_update_status_reg(temp["scheme_revision"], temp["user_query_interval_revision"])
        db_sch.sch_ver_update_all_user_query_revision(temp["user_query_interval_revision"])

        # REG_SCH
        db_reg.reg_sch_update_all_user_query_revision(temp["user_query_interval_revision"])

        db_reg.reg_sch_block_false()
        return True
    else:
        db_reg.reg_sch_block_false()
        return False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

conn = connect()
db_gui = Gui(conn)
db_pf = Pf(conn)
db_reg = Reg_sch(conn)
db_sch = Sch_ver(conn)


vvk_id = None # Необходима для исколючения
t3 = T3
try:
# регистрация ВВК
    while True:
        vvk_id, _, _, _ = db_sch.sch_ver_select_vvk_details()
        if vvk_id:
            logger.info("Есть зарегистрированная VVkScheme")
            break
        agent_ids, agents_reg_ids = db_gui.gui_select_agents_reg()
        if agents_reg_ids == []:
            logger.info("Загрузите JoinSCheme")
        else:
            if len(agent_ids) != len(agents_reg_ids):
                logger.info("Не все агенты зарегистрированы!")
            else:
                if forming_registration_vvk():
                    break
        time.sleep(t3)

# передача ПФ
    while True:
        t3 = T3
        start_time = time.time()
        scheme_revision_date_create, date_create = db_sch.sch_ver_select_date_create_unreg()
        print("!!!!!!!!", scheme_revision_date_create, date_create)
        if date_create:
            params = db_pf.pf_select_params_json_unreg(date_create, INT_LIMIT)
        else:
            params = db_pf.pf_select_params_json(INT_LIMIT)
        if len(params) > 0:
            result_id, value = parse_value(params)
            vvk_id, scheme_revision, user_query_interval_revision, t3 = db_sch.sch_ver_select_vvk_details()
            t3 = t3 if t3 is not None else T3
            result = {
                "scheme_revision": scheme_revision,
                "user_query_interval_revision": user_query_interval_revision,
                "value": value
            }
            start_request_time = time.time()
            if request_pf(result, vvk_id):
                updated_rows = db_pf.pf_update_sent_status(result_id)
                db_gui.gui_update_value(vvk_id, None, False)
                count_sent_false = db_pf.pf_select_count_sent_false()
                logger.info("DB(pf): изменено строк (true): %d | ОСТАЛОСЬ в БД: %d", updated_rows, count_sent_false)
                if count_sent_false > INT_LIMIT:
                    t3 = 0
            end_request_time = time.time()
            logger.info("Время формирование ПФ: %.4f | время отправки: %.4f", start_request_time-start_time, end_request_time-start_request_time)
        else:
            if date_create:
                if forming_re_registration_vvk():
                    logger.info("Успешная перегистрация")
                    t3 = 5
                else:
                    db_sch.sch_ver_update_status_reg_null(scheme_revision_date_create)
                    logger.error("Не успешная перегистрация!!!")
                    t3 = 5
            else:
                logger.info("В БД нет новых данных")


        end_time = time.time()
        time_transfer = end_time - start_time
        time_transfer = t3 if time_transfer > t3 else time_transfer

        time.sleep(t3 - time_transfer)

except Exception as e:
    db_reg.reg_sch_block_false()
    error_str = str(e)
    if vvk_id:
        db_gui.gui_update_value(vvk_id, error_str, False)
    logger.error("Произошла ошибка: %s", error_str)
    disconnect(conn)
    sys.exit(1)