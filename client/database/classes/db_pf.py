from logger.logger import logger


class Pf:

# _______________ PF _______________

# __ Create Table + Index __
    def pf_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS pf (
                    id BIGSERIAL PRIMARY KEY,
                    item_id INT NOT NULL,
                    metric_id VARCHAR(100) NOT NULL,
                    t BIGINT NOT NULL,
                    v VARCHAR(100) NOT NULL,
                    etmax BOOLEAN,
                    etmin BOOLEAN,
                    comment VARCHAR(100)
                );
            """
            cur.execute(sql_create_table)
            sql_create_index2 = "CREATE INDEX idx_pf_t ON pf using BRIN (t);"
            cur.execute(sql_create_index2)
            self.conn.commit()
            logger.info("DB(pf): таблица создана")
            return True
        except Exception as e:
            logger.error("DB(pf): pf_create_table: %s", e)
            raise e

# __ Drop Table + Index __
    def pf_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_index2 = "DROP INDEX IF EXISTS idx_pf_t;"
            cur.execute(sql_drop_index2)
            sql_drop_table = "DROP TABLE IF EXISTS pf;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(pf): таблица удалена")
            return True
        except Exception as e:
            logger.error("DB(pf): pf_drop_table: %s", e)
            raise e


# __ Select  __
    # !!!
    def pf_select_params_json(self, int_limit: int = 20000) -> list:
        """
            SQL-запрос: Получить ПФ (неотправленные).

        Args:
            int_limit (int, optional): Максимальное количество записей для выборки. По умолчанию 20000.

        Returns:
            list: Список словарей, где каждый словарь представляет одну запись из таблицы PF.
                  Ключи словаря - это имена столбцов, значения - соответствующие данные записи.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select_params = (f"SELECT id, item_id, metric_id, t, v, etmax, etmin, comment FROM pf "
                                 f"ORDER BY t LIMIT {int_limit};")
            cur.execute(sql_select_params)
            self.conn.commit()
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = []
            for row in data:
                item = {}
                for i, value in enumerate(row):
                    if value is not None:
                        item[columns[i]] = value
                result.append(item)
            return result
        except Exception as e:
            logger.error("DB(pf): pf_select_params_json: %s", e)
            raise e

    # !!!
    def pf_select_params_json_unreg(self, time_create: int, int_limit: int = 20000) -> list:
        """
            SQL-запрос: Получить ПФ (неотправленные) для старой схему ВВК.

        Args:
            time_create (int): Время регистрации следующей схемы ВВК.
            int_limit (int, optional): Максимальное количество записей для выборки. По умолчанию 20000.

        Returns:
            list: Список словарей, где каждый словарь представляет одну запись из таблицы PF.
                  Ключи словаря - это имена столбцов, значения - соответствующие данные записи.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select_params = (f"SELECT id, item_id, metric_id, t, v, etmax, etmin, comment FROM pf "
                                 f"WHERE t < {time_create} ORDER BY t LIMIT {int_limit};")
            cur.execute(sql_select_params)
            self.conn.commit()
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = []
            for row in data:
                item = {}
                for i, value in enumerate(row):
                    if value is not None:
                        item[columns[i]] = value
                result.append(item)
            return result
        except Exception as e:
            logger.error("DB(pf): pf_select_params_json: %s", e)
            raise e

    # !!!
    def pf_select_count_sent_false(self) -> int:
        """
            SQL-запрос: Считает количество неотправленных записей.

        Returns:
            int: Количество записей со статусом sent = False.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf WHERE sent = False;"
            cur.execute(sql_count_rows)
            remaining_rows = int(cur.fetchone()[0])
            return remaining_rows
        except Exception as e:
            logger.error("DB(pf): pf_select_count_sent_false: %s", e)
            raise e

    def pf_select_count_all(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf;"
            cur.execute(sql_count_rows)
            remaining_rows = cur.fetchone()[0]
            return remaining_rows
        except Exception as e:
            logger.error("DB(pf): pf_select_count_all: %s", e)
            raise e

# __ Insert __

# __ Update __
    # !!!
    def pf_update_sent_status(self, id_list: list) -> int:
        """
            SQL-запрос: Обновляет у ПФ статус на отправлено.

        Args:
            id_list (list): Список идентификаторов записей, для которых нужно обновить статус.

        Returns:
            int: Количество обновленных записей.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            id_string = ','.join(map(str, id_list))
            sql_update_params = f"UPDATE pf SET sent = TRUE WHERE id IN ({id_string});"
            cur.execute(sql_update_params)
            updated_rows = cur.rowcount
            self.conn.commit()
            return updated_rows
        except Exception as e:
            logger.error("DB(pf): pf_update_sent_status: %s", e)
            raise e

# __ Delete __
    def pf_delete_params(self, one_day_ago_timestamp: int) -> int:
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM pf WHERE t < {one_day_ago_timestamp};"
            cur.execute(sql_delete_params)
            deleted_rows = cur.rowcount
            self.conn.commit()
            return deleted_rows
        except Exception as e:
            logger.error("DB(pf): pf_delete_params: %s", e)
            raise e

    # !!!
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
            logger.error("DB(pf): pf_delete_records: %s", e)
            raise e






