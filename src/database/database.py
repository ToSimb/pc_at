import json
import datetime
import time

from logger.logger import logger


class Database:
    def __init__(self, conn):
        self.conn = conn



    def select_last_agents_reg(self, name_table: str, limit: int) -> list:
        try:
            cur = self.conn.cursor()
            sql_select_last_50_agents_reg_id = f"SELECT * FROM {name_table} ORDER BY id DESC LIMIT {limit};"
            cur.execute(sql_select_last_50_agents_reg_id)
            rows = cur.fetchall()
            self.conn.commit()
            columns = [desc[0] for desc in cur.description]
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            logger.error("общая DB: ошибка получения последних 50 строк: %s", e)
            raise e

# ______________ GUI _______________
# __ Select __
    def gui_select_agents_reg(self) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select_agent_reg_id = "SELECT number_id, agent_reg_id FROM gui WHERE type_id = TRUE;"
            cur.execute(sql_select_agent_reg_id)
            rows = cur.fetchall()
            number_id = [row[0] for row in rows if row[0] is not None]
            agent_reg_id = [row[1] for row in rows]
            self.conn.commit()
            return number_id, agent_reg_id
        except Exception as e:
            logger.error("DB(gui): gui_select_agents_reg: %s", e)
            raise e

    def gui_select_check_agent_reg_id(self, agent_reg_id: str) -> int:
        try:
            cur = self.conn.cursor()
            sql_select_check = "SELECT number_id FROM gui WHERE type_id = TRUE AND agent_reg_id = %s;"
            cur.execute(sql_select_check, (agent_reg_id,))
            result = cur.fetchall()
            self.conn.commit()
            if result:
                return result[0][0]
            else:
                raise Exception("Такого быть не может!")
        except Exception as e:
            logger.error("DB(gui): gui_select_check_agent_reg_id: %s", e)
            raise e

# __ Insert __
    def gui_insert_join_scheme(self, vvk_name: str, agent_reg_id: list):
        try:
            cur = self.conn.cursor()
            sql_insert1 = "INSERT INTO gui (vvk_name, type_id) VALUES (%s,%s);"
            cur.execute(sql_insert1, (vvk_name, False))
            sql_insert2 = "INSERT INTO gui (agent_reg_id) VALUES (%s);"
            cur.executemany(sql_insert2, [(agent_id,) for agent_id in agent_reg_id])
            self.conn.commit()
            logger.info("DB(gui): JoinScheme загружена")
            return True
        except Exception as e:
            logger.error("DB(gui): gui_insert_join_scheme: %s", e)
            raise e

# __ Update _
    def gui_update_agent_reg(self, agent_id: int, agent_reg_id: str, status_reg: bool, error_reg: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET number_id = %s, status_reg = %s, time_reg = %s, error_reg = %s WHERE agent_reg_id = %s;"
            cur.execute(sql_update_gui, (agent_id, status_reg, time_reg, error_reg, agent_reg_id))
            self.conn.commit()
            logger.info(f"DB(gui): agent_reg_id '{agent_reg_id}' статус изменен: {status_reg}")
            if error_reg:
                logger.error(f"DB(gui):  agent_reg_id '{agent_reg_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            logger.error("DB(gui): gui_update_agent_reg - agent_reg_id %s : %s", agent_reg_id, e)
            raise e

    def gui_update_vvk_reg(self, vvk_id: int, status_reg: bool, error_reg: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET number_id = %s, status_reg = %s, time_reg = %s, error_reg = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_gui, (vvk_id, status_reg, time_reg, error_reg))
            self.conn.commit()
            logger.info(f"DB(gui): agent_reg_id '{vvk_id}' статус изменен: {status_reg}")
            if error_reg:
                logger.error(f"DB(gui):  agent_reg_id '{vvk_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            logger.error("DB(gui): gui_update_vvk_reg - vvk_id %s : %s", vvk_id, e)
            raise e

    def gui_update_value(self, agent_id: int, error_value: str, type_id: bool) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_value = %s, error_value = %s WHERE number_id = %s AND type_id = %s;"
            cur.execute(sql_update_gui, (time_reg, error_value, agent_id, type_id))
            self.conn.commit()
            if error_value:
                if type_id:
                    logger.error(f"DB(gui): ошибка приема ПФ agent_id '{agent_id}': {error_value}")
                else:
                    logger.error(f"DB(gui): ошибка приема ПФ vvk_id '{agent_id}': {error_value}")
            return True
        except Exception as e:
            self.conn.rollback()
            if type_id:
                logger.error("DB(gui): gui_update_value - agent_id %s: %s", agent_id, e)
            else:
                logger.error("DB(gui): gui_update_value - vvk_id %s: %s", agent_id, e)
            raise e

# __ Delete __
    def gui_delete(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete = f"DELETE FROM gui;"
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info("DB(gui): таблица очищена")
            return True
        except Exception as e:
            logger.error("DB(gui): gui_delete: %s", e)
            raise e

# ____________ REG_SCH _____________

# __ Select __
    # __ VVK __
    def reg_sch_select_vvk_scheme(self):
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT scheme_revision, scheme, metric_info_list FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            result = cur.fetchone()
            if result:
                return result
            else:
                raise Exception("VvkScheme не зарегистирована!!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_scheme: %s", e)
            raise e

    def reg_sch_select_vvk_all(self) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT user_query_interval_revision, original_scheme, scheme, metric_info_list FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            result = cur.fetchone()
            if result:
                return result
            else:
                raise Exception("VvkScheme не зарегистирована!!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_scheme_all: %s", e)
            raise e

    def reg_sch_select_vvk_all_json(self) -> dict:
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            self.conn.commit()
            data = cur.fetchall()
            result = {
                "scheme_revision": data[0][0],
                "user_query_interval_revision": data[0][1],
                "original_scheme": data[0][2],
                "scheme": data[0][3],
                "metric_info_list": data[0][4]
            }
            if result:
                return result
            else:
                raise Exception("VvkScheme не зарегистирована!!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_full: %s", e)
            raise e

    def reg_sch_select_check_vvk(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_check = "SELECT COUNT(*) FROM reg_sch WHERE type_id = FALSE;"
            cur.execute(sql_check)
            count = cur.fetchone()[0]
            self.conn.commit()
            if count > 0:
                return True
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_check_vvk: %s", e)
            raise e

    # __ AGENTS __
    def reg_sch_select_count_agents(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_count_agents = "SELECT COUNT(*) FROM reg_sch WHERE type_id = TRUE;"
            cur.execute(sql_count_agents)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_count_agents: %s", e)
            raise

    def reg_sch_select_metrics_ids(self, agent_id: int) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_query = f"SELECT scheme_revision, user_query_interval_revision, jsonb_array_elements(scheme->'metrics')->>'metric_id' AS metric_id FROM reg_sch WHERE number_id = {agent_id};"
            cur.execute(sql_query)
            result = cur.fetchall()
            self.conn.commit()
            if result:
                scheme_revision = result[0][1]
                user_query_interval_revisions = result[0][0]
                metric_ids = [row[2] for row in result]
                return scheme_revision, user_query_interval_revisions, metric_ids
            return None, None, []
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_metrics_ids: %s", e)
            raise e

# __ Insert __
    def reg_sch_insert_vvk(self, scheme_revision: int, original_scheme: dict, scheme: dict, metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_insert_scheme = (
                "INSERT INTO reg_sch (type_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list) "
                "VALUES (FALSE, %s, %s, %s, %s, %s);")
            cur.execute(sql_insert_scheme, (scheme_revision, 0, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list)))
            self.conn.commit()
            logger.info("DB(reg_sch): VvkScheme зарегистрирована")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_insert_vvk: %s", e)
            raise e

    def reg_sch_insert_agent(self, number_id: int, scheme_revision: int, user_query_interval_revision: int, original_scheme: dict, scheme: dict, metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_insert = ("INSERT INTO reg_sch (type_id, number_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list) "
                                 "VALUES (TRUE, %s, %s, %s, %s, %s, %s);")
            cur.execute(sql_insert, (number_id, scheme_revision, user_query_interval_revision, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list)))
            self.conn.commit()
            logger.info(f"DB(reg_sch): Agent '{number_id}' зарегистрирован")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_insert_agent '%s': %s", number_id, e)
            raise e


# __ Update __
    def reg_sch_update_vvk_scheme(self, scheme: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update_scheme = "UPDATE reg_sch SET scheme = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_scheme, (json.dumps(scheme),))
            logger.info("DB(reg_sch): VvkScheme-scheme изменена")
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_vvk_scheme: %s", e)
            raise e

    def reg_sch_update_vvk_id(self, vvk_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE reg_sch SET number_id = {vvk_id} WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info(f"DB(reg_sch): значение vvk_id '{vvk_id}' успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_vvk_id: %s", e)
            raise e

    def reg_sch_update_all_user_query_revision(self, user_query_interval_revision: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE reg_sch SET user_query_interval_revision = {user_query_interval_revision};"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение user_query_interval_revision успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_all_user_query_revision: %s", e)
            raise e

# __ Delete __


# __ BLOCK __
    def reg_sch_block_true(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = "UPDATE reg_sch SET block = TRUE WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение block успешно изменено на True")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_block_true: %s", e)
            raise e

    def reg_sch_block_false(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = "UPDATE reg_sch SET block = FALSE WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение block успешно изменено на False")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_block_false: %s", e)
            raise e

    def reg_sch_block_check(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_query = "SELECT block FROM reg_sch WHERE type_id = FALSE;"
            cur.execute(sql_query)
            self.conn.commit()
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_check_block: %s", e)
            raise e


# _______________ PF _______________

# __ Insert _
    def pf_insert_params(self, data: list) -> bool:
        try:
            with self.conn.cursor() as cur:
                sql_insert_data = "INSERT INTO pf (item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s);"
                cur.executemany(sql_insert_data, data)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("DB(pf): pf_insert_params: %s", e)
            raise e

# ____________ SCH_VER _____________

# __ Insert __
    def sch_ver_insert_vvk(self, data: dict) -> bool:
        try:
            current_time = int(time.time())
            cur = self.conn.cursor()
            sql_create = (
                "INSERT INTO sch_ver (vvk_id, scheme_revision, user_query_interval_revision, date_create, status_reg) "
                "VALUES (%s,%s,%s,%s,%s);")
            cur.execute(sql_create, (
            data["vvk_id"], data["scheme_revision"], data["user_query_interval_revision"], current_time, True))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_insert_vvk_scheme: ошибка при регистации vvk_scheme у AF: %s", e)
            raise e