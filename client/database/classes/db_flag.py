import datetime

from logger.logger import logger

class Flag:

    # __ Create Table __
    def flag_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                    CREATE TABLE IF NOT EXISTS flag (
                        id SERIAL PRIMARY KEY,
                        flag BOOLEAN DEFAULT FALSE
                    );
                """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(flag): таблица создана")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(flag): flag_create_table: %s", e)
            raise e

    # __ Drop Table __
    def flag_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS flag;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(flag): таблица удалена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(flag): flag_drop_table: %s", e)
            raise e

    # __ Select Table __

    # __ Insert Table __
    def flag_insert(self) -> None:
        try:
            cur = self.conn.cursor()
            sql_insert_flag = "INSERT INTO flag (flag) VALUES (%s)"
            cur.execute(sql_insert_flag, (False,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(flag): flag_insert: %s", e)
            raise e

    # __ Update Table __
