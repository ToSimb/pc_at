from typing import Union

from logger.logger import logger

class Database:
    def __init__(self, conn):
        self.conn = conn

# _______________ PF _______________
    def pf_create_table(self):
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS PF (
                    id BIGSERIAL PRIMARY KEY,
                    vvk_id INT NOT NULL,
                    scheme_revision INT NOT NULL,
                    user_query_interval_revision INT NOT NULL,
                    item_id INT NOT NULL,
                    metric_id VARCHAR(100) NOT NULL,
                    t INT NOT NULL,
                    v VARCHAR(100) NOT NULL,
                    etmax BOOLEAN,
                    etmin BOOLEAN,
                    comment VARCHAR(100),
                    sent BOOLEAN DEFAULT FALSE
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("Таблица 'PF' создана")
            return True
        except Exception as e:
            logger.error("Ошибка при создании таблицы 'pf': %s", e)
            return False

    def pf_drop_table(self):
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS PF;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("Таблица 'PF' удалена")
            return True
        except Exception as e:
            logger.error("Ошибка при удалении таблицы 'PF': %s", e)
            return False

    def pf_execute_params_one(self,
                       vvk_id: int,
                       scheme_revision: int,
                       user_query_interval_revision: int,
                       item_id: int,
                       metric_id: str,
                       t: int,
                       v: str,
                       etmax: bool,
                       etmin: bool,
                       comment: str):
        try:
            with self.conn.cursor() as curs:
                sql_insert_data = " INSERT INTO pf (vvk_id, scheme_revision, user_query_interval_revision, item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                curs.execute(sql_insert_data, (
                vvk_id, scheme_revision, user_query_interval_revision, item_id, metric_id, t, v, etmax, etmin, comment))
            self.conn.commit()
        except Exception as e:
            logger.error("Ошибка БД - не удалось сделать execute_params: %s", e)
            return None

    def pf_execute_params(self, data):
        try:
            with self.conn.cursor() as curs:
                sql_insert_data = " INSERT INTO pf (vvk_id, scheme_revision, user_query_interval_revision, item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                curs.executemany(sql_insert_data, data)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("Ошибка БД - не удалось сделать executemany_params: %s", e)
            return False

    def pf_delete_params(self, one_day_ago_timestamp: int):
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM pf WHERE t < {one_day_ago_timestamp};"
            cur.execute(sql_delete_params)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("Ошибка БД - не удалось удалить лишние строки: %s", e)
            return False

    def pf_select_params(self):
        try:
            cur = self.conn.cursor()
            sql_select_params = "SELECT * FROM pf;"
            cur.execute(sql_select_params)
            data = cur.fetchall()
            return data
        except Exception as e:
            logger.error("Ошибка при чтении данных из таблицы: %s", e)
            return False

    def pf_select_params_all_json(self):
        try:
            cur = self.conn.cursor()
            sql_select_params = "SELECT * FROM pf;"
            cur.execute(sql_select_params)
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = []
            for row in data:
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            logger.error("Ошибка при чтении данных из таблицы: %s", e)
            return False

    def pf_select_params_json(self, int_limit: int = 30000):
        try:
            cur = self.conn.cursor()
            sql_select_params = f"SELECT * FROM pf WHERE sent = False ORDER BY t LIMIT {int_limit};"
            cur.execute(sql_select_params)
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = []
            for row in data:
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            logger.error("Ошибка при чтении данных из таблицы: %s", e)
            return False

    def pf_update_sent_status(self, id_list):
        try:
            logger.info("передан запрос")
            cur = self.conn.cursor()
            sql_update_params = "UPDATE pf SET sent = TRUE WHERE id IN %s;"
            id_tuple = tuple(id_list)
            cur.execute(sql_update_params, (id_tuple,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("Ошибка БД - не удалось обноовить строки: %s", e)
            return False

    def pf_count_cent_false(self):
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf WHERE sent = False;"
            cur.execute(sql_count_rows)
            remaining_rows = cur.fetchone()[0]
            return remaining_rows
        except Exception as e:
            logger.error("Ошибка при подсчете оставшихся строк в таблице: %s", e)
            return False

    def pf_count_all(self):
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf;"
            cur.execute(sql_count_rows)
            remaining_rows = cur.fetchone()[0]
            return remaining_rows
        except Exception as e:
            logger.error("Ошибка при подсчете строк в таблице: %s", e)
            return False
