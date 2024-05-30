import time
import json

from logger.logger import logger


class Sch_ver:
    def __init__(self, conn):
        self.conn = conn

# ____________ SCH_VER _____________

# __ Create Table __
    def sch_ver_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS sch_ver (
                    id SERIAL PRIMARY KEY,
                    vvk_id INT,
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    date_create BIGINT,
                    t3 INT,
                    status_reg BOOLEAN DEFAULT FALSE,
                    scheme JSONB,
                    metric_info_list JSONB
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(sch_ver): таблица создана")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_create_table: %s", e)
            raise e

# __ Drop Table __
    def sch_ver_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS sch_ver;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(sch_ver): таблица удалена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_drop_table: %s", e)
            raise e

# __ Select __
    def sch_ver_select_vvk_details(self) -> tuple:
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
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_select_vvk_scheme: %s", e)
            raise e

    def sch_ver_select_date_create_unreg(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_select = (
                "SELECT scheme_revision, date_create FROM sch_ver "
                "WHERE status_reg = FALSE "
                "ORDER BY date_create "
                "LIMIT 1"
            )
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result[0], result[1]
            else:
                return None, None
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_select_date_create: %s", e)
            raise e

    def sch_ver_select_vvk_details_unreg(self) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = (
                "SELECT vvk_id, scheme_revision, scheme, metric_info_list FROM sch_ver "
                "WHERE status_reg = FALSE "
                "ORDER BY date_create "
                "LIMIT 1"
            )
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result
            else:
                return (None, None, None, None)
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_select_vvk_details_unreg: %s", e)
            raise e

    def sch_ver_select_latest_status(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_select = (
                "SELECT status_reg FROM sch_ver "
                "ORDER BY id DESC "
                "LIMIT 1"
            )
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): get_latest_status: %s", e)
            raise e

# __ Insert __
    def sch_ver_insert_vvk(self, first_reg: bool, data: dict, scheme: dict, metric_info_list) -> bool:
        try:
            current_time = int(time.time())
            cur = self.conn.cursor()
            sql_create = ("INSERT INTO sch_ver (vvk_id, scheme_revision, user_query_interval_revision, date_create, status_reg, scheme, metric_info_list) "
                          "VALUES (%s,%s,%s,%s,%s,%s,%s);")
            cur.execute(sql_create, (data["vvk_id"], data["scheme_revision"], data["user_query_interval_revision"],
                                     current_time, first_reg, json.dumps(scheme), json.dumps(metric_info_list)))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_insert_vvk_scheme: ошибка регистации vvk_scheme у AF: %s", e)
            raise e

# __ Update __
    def sch_ver_update_status_reg(self, scheme_revision: int, user_query_interval_revision: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = (
                "UPDATE sch_ver "
                "SET status_reg = TRUE "
                "WHERE scheme_revision = %s AND user_query_interval_revision = %s"
            )
            cur.execute(sql_update, (scheme_revision, user_query_interval_revision))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_update_status_reg: ошибка обновления status_reg: %s", e)
            raise e

    def sch_ver_update_status_reg_null(self, scheme_revision: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = (
                "UPDATE sch_ver "
                "SET status_reg = NULL "
                f"WHERE scheme_revision = {scheme_revision} "
            )
            cur.execute(sql_update, )
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_update_status_reg_null: ошибка обновления status_reg: %s", e)
            raise e

    def sch_ver_update_all_user_query_revision(self, user_query_interval_revision: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE sch_ver SET user_query_interval_revision = {user_query_interval_revision};"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(sch_ver): значение user_query_interval_revision успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_update_all_user_query_revision: %s", e)
            raise e

# __ Delete __

    def sch_ver_delete_vvk_no_reg(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete = (
                "DELETE FROM sch_ver "
                "WHERE ctid = (SELECT ctid FROM sch_ver WHERE status_reg = FALSE ORDER BY date_create LIMIT 1);"
            )
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info(f"DB(sch_ver): Удалена не удачная версия Vvk Scheme")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_delete_vvk_no_reg: %s", e)
            raise e