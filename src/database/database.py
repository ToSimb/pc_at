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

    def gui_delete(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM gui;"
            cur.execute(sql_delete_params)
            self.conn.commit()
            logger.info("DB(gui): таблица очищена")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка удаления строк: %s", e)
            raise e
    def gui_registration_join_scheme(self, vvk_name: str, agent_reg_id: list) -> bool:
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
            self.conn.rollback()
            logger.error("DB(gui): ошибка загрузки JoinScheme: %s", e)
            raise e
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
            logger.error("DB(gui): ошибка получения agent_reg_id: %s", e)
            raise e
    def gui_registration_agent(self, agent_id: int, agent_reg_id: str, status_reg: bool, error_reg: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET number_id = %s, status_reg = %s, time_reg = %s, error_reg = %s WHERE agent_reg_id = %s;"
            cur.execute(sql_update_gui, (agent_id, status_reg, time_reg, error_reg, agent_reg_id))
            self.conn.commit()
            logger.info(f"DB(gui): agent_reg_id '{agent_reg_id}' статус изменен: {status_reg}")
            if error_reg:
                logger.error(f"DB(gui):ошибка регистации agent_reg_id {agent_reg_id}': {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): ошибка регистации agent_reg_id %s : %s", agent_reg_id, e)
            raise e

    def gui_params_reg_value(self, agent_id: int, error_value: str, type_id: bool) -> bool:
        try:
            print("asASD", type_id )
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_value = %s, error_value = %s WHERE number_id = %s AND type_id = %s;"
            cur.execute(sql_update_gui, (time_reg, error_value, agent_id, type_id))
            self.conn.commit()
            if error_value:
                logger.error(f"DB(gui): ошибка приема ПФ agent_id '{agent_id}': {error_value}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): ошибка работы БД при вызове gui_params_reg_value: %s", e)
            raise e

    def gui_registration_vvk(self, vvk_id: int, status_reg: bool, error_reg: str) -> bool:
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
            logger.error("DB(gui): ошибка регистации vvk_id %s : %s", vvk_id, e)
            raise e


# ____________ REG_SCH _____________

    def reg_sch_registration_vvk_scheme(self, scheme_revision: int, original_scheme: dict, scheme: dict, metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_check_existence = "SELECT COUNT(*) FROM reg_sch WHERE type_id = FALSE;"
            cur.execute(sql_check_existence)
            count = cur.fetchone()[0]
            self.conn.commit()
            if count > 0:
                print("Переригистрация VvkScheme еще не сделана!!!")
                self.conn.commit()
                raise Exception("Переригистрация VvkScheme еще не сделана!!!")
            else:
                sql_insert_scheme = ("INSERT INTO reg_sch (type_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list) "
                                     "VALUES (FALSE, %s, %s, %s, %s, %s);")
                cur.execute(sql_insert_scheme, (scheme_revision, 0, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list)))
                self.conn.commit()
                logger.info("DB(reg_sch): VvkScheme зарегистрирована")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): ошибка регистрации VvkScheme: %s", e)
            raise e

    def reg_sch_select_vvk_schemes(self) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT user_query_interval_revision, original_scheme, scheme, metric_info_list FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            result = cur.fetchone()
            if result:
                return result
            else:
                print("VvkScheme не зарегистирована!!")
                raise Exception("VvkScheme не зарегистирована!!")

        except Exception as e:
            logger.error("DB(reg_sch): ошибка при получении схемы из БД: %s", e)
            raise e

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
            logger.error("DB(reg_sch): ошибка при получении схемы из БД: %s", e)
            raise e

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
            logger.error("DB(reg_sch): ошибка при изменении VvkScheme-scheme: %s", e)
            raise e

    def reg_sch_update_number_vvk(self, vvk_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE reg_sch SET number_id = {vvk_id} WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение vvk_id успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): ошибка при изменении значения vvk_id: %s", e)
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
            logger.error("DB(reg_sch): ошибка при изменении значения user_query_interval_revision: %s", e)
            raise e

    def reg_sch_select_full_vvk(self):
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
            return result
        except Exception as e:
            logger.error("DB(reg_sch): ошибка при получении full_vvk из БД: %s", e)
            raise e


    def reg_sch_count_agents(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_count_agents = "SELECT COUNT(*) FROM reg_sch WHERE type_id = TRUE;"
            cur.execute(sql_count_agents)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            logger.error("DB(reg_sch): Ошибка при получении количества зарегистрированных агентов: %s", e)
            raise e


    def reg_sch_registration_agent(self, number_id: int, scheme_revision: int, user_query_interval_revision: int, original_scheme: dict, scheme: dict, metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_check_existence = f"SELECT COUNT(*) FROM reg_sch WHERE number_id = {number_id};"
            cur.execute(sql_check_existence)
            count = cur.fetchone()[0]
            self.conn.commit()
            if count > 0:
                sql_update = f"UPDATE reg_sch SET scheme_revision = %s, user_query_interval_revision = %s, original_scheme = %s, scheme = %s, metric_info_list = %s WHERE number_id = {number_id}"
                cur.execute(sql_update, (scheme_revision, user_query_interval_revision, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list),))
                self.conn.commit()
                logger.info(f"DB(reg_sch): Agent '{number_id}' перезарегистрирована")
            else:
                sql_insert = ("INSERT INTO reg_sch (type_id, number_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list) "
                                     "VALUES (TRUE, %s, %s, %s, %s, %s, %s);")
                cur.execute(sql_insert, (number_id, scheme_revision, user_query_interval_revision, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list)))
                self.conn.commit()
                logger.info(f"DB(reg_sch): Agent '{number_id}' зарегистрирована")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): ошибка регистрации agenta '%s': %s", number_id, e)
            raise e


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
            logger.error("DB(reg_sch): ошибка при изменении значения block - True: %s", e)
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
            logger.error("DB(reg_sch): ошибка при изменении значения block - False: %s", e)
            raise e

    def reg_sch_check_block(self) -> bool:
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
            logger.error("DB(reg_sch): ошибка получения значения block: %s", e)
            raise e


    def reg_sch_get_metrics_ids(self, agent_id) -> list:
        try:
            cur = self.conn.cursor()
            sql_query = f"SELECT scheme_revision, user_query_interval_revision, jsonb_array_elements(scheme->'metrics')->>'metric_id' AS metric_id FROM reg_sch WHERE number_id = {agent_id} AND type_id = True;;"
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
            logger.error("DB(reg_sch): ошибка получения идентификаторов метрик: %s", e)
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
            self.conn.rollback()
            logger.error("DB(pf): ошибка записи ПФ: %s", e)
            raise e

# ____________ SCH_VER _____________
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