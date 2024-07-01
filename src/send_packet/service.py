import httpx
import requests

from config import PF_LIMIT, DEBUG, PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT

from logger.logger_send import logger_send

from database.database import Database



# !!! Надо переделатеть !!!
async def send_value_to_url(vvk_id, packet: dict):
    async with httpx.AsyncClient() as client:
        url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
        headers = {'Content-Type': 'application/json'}
        if DEBUG:
            url = f'http://localhost:8000/test/params?vvk_id={vvk_id}'
        try:
            response = await client.post(url, json=packet, headers=headers)
            print(response.status_code)
            return response.status_code
        except Exception as e:
            logger_send.error(f"An error occurred: {e}")


def requestjson_1(vvk_id, packet: dict, db):
    url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
    headers = {'Content-Type': 'application/json'}
    if DEBUG:
        url = f'http://localhost:8000/test/params?vvk_id={vvk_id}'
    try:
        response = requests.post(url, json=packet, headers=headers)
        if response.status_code == 200:
            print("Данные успешно отправлены.")
            return True
        elif response.status_code == 227:
            print("Данные отправлены, но ошибка 227")
            return True
        else:
            error_str = str(response.status_code) + " : " + str(response.text)
            db.gui_update_value(vvk_id, error_str, False)
            raise Exception(error_str)
    except requests.RequestException as e:
        error_str = str(e)
        db.gui_update_value(vvk_id, error_str, False)
        print(f"Произошла ошибка при отправке запроса: {e}")
        return False


def get_params_from_db_by_number_id(number_id: int, db: Database) -> tuple:
    result_id = []
    params = []
    index_row = 0
    ans = db.pf_select_pf_of_1_packet(number_id, index_row)
    if ans is None:
        return None, None
    result_id.append(ans[0])
    len_pf = ans[1]
    params += ans[2]
    while True:
        index_row += 1
        ans = db.pf_select_pf_of_1_packet(number_id, index_row)
        if ans is None:
            break
        len_pf += ans[1]
        if len_pf > int(PF_LIMIT):
            break
        result_id.append(ans[0])
        params += ans[2]
    return result_id, params, len_pf

def parse_value(params: list) -> list:
    """
        Парсит и собирает ПФ по item_id и metric_id.

    Args:
        params (list): Список ПФ, содержащих параметры.

    Returns:
        list: Value для отправки (output_data).
    """
    result = {}
    for item in params:

        item_id = item['item_id']
        metric_id = item['metric_id']
        t = item['t']
        v = item['v']
        comment = item.get('comment')
        etmax = item.get('etmax')
        etmin = item.get('etmin')

        key = (item_id, metric_id)
        if key not in result:
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

        result[key]['data'].append(data_item)

    output_data = sorted(result.values(), key=lambda x: (x['item_id'], x['metric_id']))

    return output_data

def forming_packet(value: list, db) -> tuple:
    vvk_id, scheme_revision, user_query_interval_revision, _ = db.sch_ver_select_vvk_details()
    result = {
        "scheme_revision": scheme_revision,
        "user_query_interval_revision": user_query_interval_revision,
        "value": value
    }
    return vvk_id, result