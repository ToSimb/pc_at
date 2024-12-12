import time
import json
import httpx

from config import MY_PORT, PF_LIMIT, DEBUG, PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT

from database.database import Database

from logger.logger_send import logger_send


def save_to_json(params, agent_id):
    # logger_send.info(f"Saving params agent '{agent_id}' to json")
    with open(f"files/pf_send/agent_{agent_id}.json", 'w', encoding='utf-8') as json_file:
        json.dump(params, json_file, ensure_ascii=False, indent=4)
async def send_value_to_url(vvk_id, number_id, packet: dict, db: Database):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=12.0)) as client:
        url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
        headers = {'Content-Type': 'application/json'}
        if DEBUG:
            url = f'http://localhost:{MY_PORT}/test/params?vvk_id={vvk_id}'
        try:
            response = await client.post(url, json=packet, headers=headers)
            logger_send.info(f"response - {response}")
            if response.status_code == 200:
                return True
            elif response.status_code == 227:
                return True
            else:
                error_str = str(response.status_code) + " : " + str(response.text)
                db.gui_update_value_out(vvk_id, number_id, error_str)
                raise Exception(error_str)
        except httpx.HTTPStatusError as e:
            error_str = f"HTTP status error: {e.request} {str(e)}"
            db.gui_update_value_out(vvk_id, number_id, error_str)
            raise Exception(error_str)
        except httpx.TimeoutException as e:
            error_str = f"A timeout error occurred: {e.request} {str(e)}"
            db.gui_update_value_out(vvk_id, number_id, error_str)
            raise Exception(error_str)
        except httpx.RequestError as e:
            error_str = f"HTTP request error occurred: {e.request} {str(e)}"
            db.gui_update_value_out(vvk_id, number_id, error_str)
            raise Exception(error_str)
        except httpx.HTTPError as e:
            error_str = f"HTTP Exception for: {e.request} {str(e)}"
            db.gui_update_value_out(vvk_id, number_id, error_str)
            raise Exception(error_str)

def get_params_from_db_by_number_id(number_id: int, db: Database) -> tuple:
    start_time = time.time()
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
        get_time = time.time()
        index_row += 1
        ans = db.pf_select_pf_of_1_packet(number_id, index_row)
        if ans is None:
            break
        len_pf += ans[1]
        if len_pf > int(PF_LIMIT):
            len_pf -= ans[1]
            break
        if get_time - start_time > 10:
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