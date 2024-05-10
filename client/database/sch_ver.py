from logger.logger import logger

class Sch_ver:
    def __init__(self, conn):
        self.conn = conn

# ____________ SCH_VER _____________
    def sch_ver_create_table(self):
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS sch_ver (
                    id SERIAL PRIMARY KEY,
                    vvk_id INT,
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    date_create INT,
                    status_reg BOOLEAN
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(sch_ver): таблица создана")
            return True
        except Exception as e:
            logger.error("DB(sch_ver): ошибка создания таблицы: %s", e)
            raise e

    def sch_ver_drop_table(self):
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