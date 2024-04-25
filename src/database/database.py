from typing import Union

from logger.logger import logger

class Database:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self):
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
        except Exception as e:
            logger.info("Ошибка при создании таблицы 'pf'", e)

    def drop_table(self):
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS PF;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("Таблица 'PF' удалена")
        except Exception as e:
            logger.info("Ошибка при удалении таблицы 'PF':", e)

    def execute_params(self,
                       vvk_id: int,
                       scheme_revision: int,
                       user_query_interval_revision: int,
                       item_id: int,
                       metric_id: str,
                       t: int,
                       v: Union[int, str],
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
            logger.info("Ошибка БД - не удалось сделать execute_params:", e)
            return None

    def delete_params(self, one_day_ago_timestamp: int):
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM pf WHERE t < {one_day_ago_timestamp};"
            cur.execute(sql_delete_params)
            self.conn.commit()
        except Exception as e:
            logger.info("Ошибка БД - не удалось удалить лишние строки:", e)
            return None

    def select_params(self):
        try:
            cur = self.conn.cursor()
            sql_select_params = "SELECT * FROM pf;"
            cur.execute(sql_select_params)
            data = cur.fetchall()
            return data
        except Exception as e:
            logger.info("Ошибка при чтении данных из таблицы:", e)
            return None

    def select_params_all_json(self):
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
            logger.info("Ошибка при чтении данных из таблицы:", e)
            return None

    def select_params_json(self, int_limit: int = 30000):
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
            logger.info("Ошибка при чтении данных из таблицы:", e)
            return None

    def update_sent_status(self, id_list):
        try:
            logger.info("передан запрос")
            cur = self.conn.cursor()
            sql_update_params = "UPDATE pf SET sent = TRUE WHERE id IN %s;"
            id_tuple = tuple(id_list)
            cur.execute(sql_update_params, (id_tuple,))
            self.conn.commit()
        except Exception as e:
            logger.info("Ошибка БД - не удалось обноовить строки:", e)
            return None

    def count_cent_false(self):
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf WHERE sent = False;"
            cur.execute(sql_count_rows)
            remaining_rows = cur.fetchone()[0]
            return remaining_rows
        except Exception as e:
            logger.info("Ошибка при подсчете оставшихся строк в таблице:", e)
            return None

    def count_all(self):
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf;"
            cur.execute(sql_count_rows)
            remaining_rows = cur.fetchone()[0]
            return remaining_rows
        except Exception as e:
            logger.info("Ошибка при подсчете строк в таблице:", e)
            return None
