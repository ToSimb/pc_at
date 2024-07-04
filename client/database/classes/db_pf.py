import pickle
import time

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
                number_id INT NOT NULL,
                len_pf INT NOT NULL,
                pf BYTEA NOT NULL,
                date_save BIGINT
                );
            """
            cur.execute(sql_create_table)
            sql_create_index1 = "CREATE INDEX idx_pf_t ON pf USING BTREE (number_id);"
            cur.execute(sql_create_index1)
            sql_create_index2 = "CREATE INDEX idx_pf_date_save ON pf USING BRIN (date_save);"
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
            sql_drop_index2 = "DROP INDEX IF EXISTS idx_pf_date_save;"
            cur.execute(sql_drop_index2)
            sql_drop_index1 = "DROP INDEX IF EXISTS idx_pf_t;"
            cur.execute(sql_drop_index1)
            sql_drop_table = "DROP TABLE IF EXISTS pf;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(pf): таблица удалена")
            return True
        except Exception as e:
            logger.error("DB(pf): pf_drop_table: %s", e)
            raise e

# __ Select  __
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

    def pf_select_has_records(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_check_exists = "SELECT 1 FROM pf LIMIT 1;"
            cur.execute(sql_check_exists)
            record_exists = cur.fetchone() is not None
            return record_exists
        except Exception as e:
            logger.error("DB(pf): pf_has_records: %s", e)
            raise e

    def pf_select_unique_number_ids(self) -> list:
        try:
            cur = self.conn.cursor()
            sql_distinct_ids = "SELECT DISTINCT number_id FROM pf;"
            cur.execute(sql_distinct_ids)
            unique_ids = [row[0] for row in cur.fetchall()]
            return unique_ids
        except Exception as e:
            logger.error("DB(pf): pf_select_unique_number_ids: %s", e)
            raise e

# __ Insert __
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
            self.conn.rollback()
            logger.error("DB(pf): pf_insert_params_of_1_packet: %s", e)
            raise e
# __ Update __

# __ Delete __
    def pf_delete_params_by_time(self, one_day_ago_timestamp: int) -> int:
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM pf WHERE date_save < {one_day_ago_timestamp};"
            cur.execute(sql_delete_params)
            deleted_rows = cur.rowcount
            self.conn.commit()
            return deleted_rows
        except Exception as e:
            logger.error("DB(pf): pf_delete_params: %s", e)
            raise e

