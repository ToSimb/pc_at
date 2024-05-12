import time

from logger.logger import logger

class Sch_ver:
    def __init__(self, conn):
        self.conn = conn

# ____________ SCH_VER _____________
    def sch_ver_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS sch_ver (
                    id SERIAL PRIMARY KEY,
                    vvk_id INT,
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    date_create INT,
                    t3 INT,
                    status_reg BOOLEAN DEFAULT FALSE
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(sch_ver): таблица создана")
            return True
        except Exception as e:
            logger.error("DB(sch_ver): ошибка создания таблицы: %s", e)
            raise e

    def sch_ver_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS sch_ver;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(sch_ver): таблица удалена")
            return True
        except Exception as e:
            logger.error("DB(sch_ver): ошибка удаления таблицы: %s", e)
            raise e

    def sch_ver_create_vvk_scheme(self, data: dict) -> bool:
        try:
            current_time = int(time.time())
            cur = self.conn.cursor()
            sql_create = ("INSERT INTO sch_ver (vvk_id, scheme_revision, user_query_interval_revision, date_create, status_reg) "
                          "VALUES (%s,%s,%s,%s,%s);")
            cur.execute(sql_create, (data["vvk_id"], data["scheme_revision"], data["user_query_interval_revision"], current_time, True))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): ошибка регистации vvk_scheme у AF: %s", e)
            raise e

    def sch_ver_select_vvk_scheme(self) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = ("SELECT vvk_id, scheme_revision, user_query_interval_revision, t3 FROM sch_ver "
                          "WHERE status_reg = TRUE ORDER BY date_create DESC LIMIT 1")
            cur.execute(sql_select, )
            result = cur.fetchone()
            if result:
                return result
            else:
                return [None, None, None, None]

        except Exception as e:
            logger.error("DB(sch_ver): ошибка при получении схемы из БД: %s", e)
            raise e