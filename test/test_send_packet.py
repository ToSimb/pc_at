import asyncio
import httpx
import sys
import os
import time
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import MY_PORT

from client.database.postgres import connect, disconnect
from client.database.db import Database

def request_send(number_id: int) -> bool:
    """
        Функция отправляет ПФ на сервер с помощью HTTP POST запроса.

    Args:
        final_result: Словарь с данными, которые нужно отправить на сервер.
        vvk_id: Идентификатор, который включается в URL запроса.

    Returns:
        bool: True, если функция выполнена успешно (статус-код 200 или 227).

    Raises:
        Exception: Если ответ сервера содержит статус-код, отличный от 200 или 227.
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """

    url = f'http://localhost:8000/test/send_packet?agent_id={number_id}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Данные успешно отправлены.")
            return True
        elif response.status_code == 227:
            print("Данные отправлены, но ошибка 227")
            return True
        else:
            error_str = "Произошла ошибка при отправке данных:" + str(response.status_code) + " : " + str(response.text)
            raise Exception(error_str)
    except requests.RequestException as e:
        print(f"Произошла ошибка при отправке данных: {e}")
        return False

async def fetch_data(session, number_id):
    url = f'http://localhost:{MY_PORT}/send_packet?agent_id={number_id}'
    try:
        response = await session.get(url)
        response.raise_for_status()
        print(f"Received response for param {number_id}: {response.text}")
    except httpx.HTTPError as e:
        print(f"Error fetching data for param {number_id}: {e}")

async def main(params):
    async with httpx.AsyncClient() as session:
        tasks = [fetch_data(session, number_id) for number_id in params]
        await asyncio.gather(*tasks)

try:
    conn = connect()
    db = Database(conn)
    start = time.time()
    list_id = db.reg_sch_select_number_id()
    for i in list_id:
        print(i)
        start_r = time.time()
        request_send(i)
        end_r = time.time()
        print(end_r - start_r)

    end_1 = time.time()
    print("Time: " + str(end_1 - start))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(list_id))
    end_2 = time.time()
    print("Time: " + str(end_2 - end_1))
    disconnect(conn)
except Exception as e:
    print(e)