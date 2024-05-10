from logger.logger import logger


class Pf:
    def __init__(self, conn):
        self.conn = conn

# _______________ PF _______________
    def pf_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS pf (
                    id BIGSERIAL PRIMARY KEY,
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
            logger.info("DB(pf): таблица создана")
            return True
        except Exception as e:
            logger.error("DB(pf): ошибка создания таблицы: %s", e)
            raise e

    def pf_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS pf;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(pf): таблица удалена")
            return True
        except Exception as e:
            logger.error("DB(pf): ошибка удаления таблицы: %s", e)
            raise e

    def pf_executemany_params(self, data) -> bool:
        try:
            with self.conn.cursor() as cur:
                sql_insert_data = "INSERT INTO pf (item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s);"
                cur.executemany(sql_insert_data, data)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("DB(pf): ошибка записи ПФ: %s", e)
            raise e

    def pf_delete_params(self, one_day_ago_timestamp: int) -> int:
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM pf WHERE t < {one_day_ago_timestamp};"
            cur.execute(sql_delete_params)
            deleted_rows = cur.rowcount
            self.conn.commit()
            return deleted_rows
        except Exception as e:
            logger.error("DB(pf): ошибка удаления строк: %s", e)
            raise e

    def pf_select_params_json(self,  int_limit: int = 20000):
        try:
            cur = self.conn.cursor()
            sql_select_params = (f"SELECT id, item_id, metric_id, t, v, etmax, etmin, comment FROM pf "
                                 f"WHERE sent = False ORDER BY t LIMIT {int_limit};")
            cur.execute(sql_select_params)
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
            logger.error("DB(pf): ошибка чтения данных: %s", e)
            raise e

    def pf_update_sent_status(self, id_list):
        try:
            cur = self.conn.cursor()
            id_string = ','.join(map(str, id_list))
            sql_update_params = f"UPDATE pf SET sent = TRUE WHERE id IN ({id_string});"
            cur.execute(sql_update_params)
            updated_rows = cur.rowcount
            self.conn.commit()
            return updated_rows
        except Exception as e:
            logger.error("DB(pf): ошибка изменения 'sent': %s", e)
            raise e

    def pf_count_cent_false(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf WHERE sent = False;"
            cur.execute(sql_count_rows)
            remaining_rows = int(cur.fetchone()[0])
            return remaining_rows
        except Exception as e:
            logger.error("DB(pf): ошибка подсчета строк (False): %s", e)
            raise e

    def pf_count_all(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_count_rows = "SELECT COUNT(*) FROM pf;"
            cur.execute(sql_count_rows)
            remaining_rows = cur.fetchone()[0]
            return remaining_rows
        except Exception as e:
            logger.error("DB(pf): ошибка подсчета строк: %s", e)
            raise e
