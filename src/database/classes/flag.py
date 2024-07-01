import datetime

from logger.logger import logger


class Flag:
    # __ Select Table __
    def flag_select(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_select_flag = "SELECT flag FROM flag LIMIT 1"
            cur.execute(sql_select_flag)
            result = cur.fetchone()
            self.conn.commit()
            if result is not None:
                flag = result[0]
                return bool(flag)
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(flag): flag_select: %s", e)
            raise e

    # __ Update Table __
    def flag_update(self) -> None:
        try:
            cur = self.conn.cursor()
            sql_update_flag = "UPDATE flag SET flag = NOT flag"
            cur.execute(sql_update_flag)
            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logger.error("DB(flag): flag_update_all: %s", e)
            raise e