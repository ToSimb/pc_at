import time
import json

from logger.logger import logger


class Sch_ver:
    # ____________ SCH_VER _____________

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
            logger.error("DB(sch_ver): sch_ver_select_vvk_scheme: %s", e)
            raise e

    def sch_ver_select_latest_status(self) -> tuple:
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
                return None
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): get_latest_status: %s", e)
            raise e

    # __ Insert __
    def sch_ver_insert_vvk(self, first_reg: bool, data: dict, scheme: dict, metric_info_list) -> bool:
        try:
            current_time = int(time.time())
            cur = self.conn.cursor()
            sql_create = (
                "INSERT INTO sch_ver (vvk_id, scheme_revision, user_query_interval_revision, date_create, status_reg, scheme, metric_info_list) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s);")
            cur.execute(sql_create, (data["vvk_id"], data["scheme_revision"], data["user_query_interval_revision"],
                                     current_time, first_reg, json.dumps(scheme), json.dumps(metric_info_list)))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_insert_vvk_scheme: ошибка регистации vvk_scheme у AF: %s", e)
            raise e