from logger.logger import logger


class Pf:
# _______________ PF _______________

# __ Insert _
    # !!!
    def pf_insert_params(self, data: list) -> bool:
        """
            SQL-запрос на вставку данных в таблицу 'pf'.

        Args:
            data (list): Список кортежей с данными для вставки. Каждый кортеж содержит значения для полей 'item_id',
                         'metric_id', 't', 'v', 'etmax', 'etmin', 'comment'.

        Returns:
            bool: Возвращает True, если вставка данных выполнена успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            with self.conn.cursor() as cur:
                sql_insert_data = "INSERT INTO pf (item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s);"
                cur.executemany(sql_insert_data, data)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("DB(pf): pf_insert_params: %s", e)
            raise e