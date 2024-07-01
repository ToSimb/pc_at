import pickle
import time

from logger.logger import logger
from logger.logger_send import logger_send

class Pf:
# _______________ PF _______________

# __ Insert _
    def pf_insert_params_of_1_packet(self, number_id: int, len_pf: int, data: list) -> bool:
        """
            SQL-запрос на вставку данных в таблицу 'pf'.

        Args:
            number_id (int): Идентификатор агента/ввк.
            len_pf (int): Длина ПФ
            data (list): Список кортежей с данными для вставки.

        Returns:
            bool: Возвращает True, если вставка данных выполнена успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            current_time = int(time.time())
            cur = self.conn.cursor()
            sql_insert_data = "INSERT INTO pf (number_id, len_pf, pf, date_save)  VALUES (%s,%s,%s,%s);"
            binary_data = pickle.dumps(data)
            cur.execute(sql_insert_data, (number_id, len_pf, binary_data, current_time))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("DB(pf): pf_insert_params_of_1_packet: %s", e)
            raise e

# __ Select  __
    def pf_select_pf_of_1_packet(self, number_id: int, row_number: int):
        """
            SQL-запрос на получение 1 записи из таблицы 'pf'.

        Args:
            number_id (int): Агент/ВВК, для которого надо получить данные.
            row_number (int): Номер строки для получения (0 для первой строки, 1 для второй и т.д.).

        Returns:
            tuple: Кортеж содержит значения для полей 'id', 'len_pf', 'pf'.
            None: Если нет данных

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select_data = ("SELECT id, len_pf, pf FROM pf "
                               "WHERE number_id = %s "
                               "ORDER BY id "
                               "LIMIT 1 "
                               "OFFSET %s")
            cur.execute(sql_select_data, (number_id, row_number))
            row = cur.fetchone()
            cur.close()
            if row is not None:
                deserialized_data = pickle.loads(row[2])
                result = (row[0], row[1], deserialized_data)
            else:
                result = None
            cur.close()
            return result
        except Exception as e:
            logger_send.error("DB(pf): pf_select_pf_of_1_packet: %s", e)
            raise e

# __ Delete __
    def pf_delete_records(self, id_list: list) -> int:
        """
            SQL-запрос: Удаляет записи из таблицы ПФ на основе списка идентификаторов.

        Args:
            id_list (list): Список идентификаторов записей, которые нужно удалить.

        Returns:
            int: Количество удаленных записей.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            id_string = ','.join(map(str, id_list))
            sql_delete_query = f"DELETE FROM pf WHERE id IN ({id_string});"
            cur.execute(sql_delete_query)
            deleted_rows = cur.rowcount
            self.conn.commit()
            return deleted_rows
        except Exception as e:
            logger_send.error("DB(pf): pf_delete_records: %s", e)
            raise e