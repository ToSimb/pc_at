import json

from logger.logger import logger


class Database:
    def __init__(self, conn):
        self.conn = conn

# ______________ GUI _______________

    def gui_delete(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM gui;"
            cur.execute(sql_delete_params)
            self.conn.commit()
            logger.info("DB(gui): таблица очищена>")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка удаления строк: %s", e)
            raise e
    def gui_execute_join_scheme(self, vvk_name: str, agent_reg_id: list) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_vkk_id = "INSERT INTO gui (vvk_name, type_id) VALUES (%s,%s);"
            cur.execute(sql_create_vkk_id, (vvk_name, False))
            sql_create_vkk_id = "INSERT INTO gui (agent_reg_id) VALUES (%s);"
            cur.executemany(sql_create_vkk_id, [(agent_id,) for agent_id in agent_reg_id])
            self.conn.commit()
            logger.info("DB(gui): JoinScheme загружена")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка загрузки JoinScheme: %s", e)
            raise e

# ____________ SCH_VER _____________

    def reg_sch_execute_join_scheme(self, scheme_revision: int, scheme: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_check_existence = "SELECT COUNT(*) FROM reg_sch WHERE agent_reg_id = 'JoinScheme';"
            cur.execute(sql_check_existence)
            count = cur.fetchone()[0]

            if count > 0:
                sql_update_scheme = "UPDATE reg_sch SET scheme_revision = %s, scheme = %s WHERE agent_reg_id = 'JoinScheme';"
                cur.execute(sql_update_scheme, (scheme_revision, json.dumps(scheme)))

            else:
                sql_insert_scheme = "INSERT INTO reg_sch (agent_reg_id, scheme_revision, scheme) VALUES ('JoinScheme', %s, %s);"
                cur.execute(sql_insert_scheme, (scheme_revision, json.dumps(scheme)))

            self.conn.commit()
            logger.info("DB(reg_sch): JoinScheme загружена")
            return True
        except Exception as e:
            logger.error("DB(reg_sch): ошибка загрузки JoinScheme: %s", e)
            raise e

# _______________ PF _______________
    def pf_executemany_params(self, data: list) -> bool:
        try:
            with self.conn.cursor() as curs:
                sql_insert_data = "INSERT INTO pf (item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s);"
                curs.executemany(sql_insert_data, data)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("DB(pf): ошибка записи ПФ: %s", e)
            raise e
