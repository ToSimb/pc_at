import json

from logger.logger import logger
from database.myException_db import MyException427_db, MyException527_db

class Reg_sch:

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

    def reg_sch_select_vvk_json(self) -> dict:
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT scheme_revision, user_query_interval_revision, scheme FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            self.conn.commit()
            data = cur.fetchall()
            if data:
                result = {
                    "scheme_revision": data[0][0],
                    "user_query_interval_revision": data[0][1],
                    "scheme": data[0][2],
                }
                return result
            else:
                raise Exception("VvkScheme не зарегистирована!!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_json: %s", e)
            raise e

    def reg_sch_select_vvk_all(self) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list FROM reg_sch WHERE type_id = FALSE"
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

    def reg_sch_select_vvk_metric_info_list(self) -> dict:
        """
        SQL-запрос для получения 'metric_info_list' схему ВВК.

        Returns:
            dict: Словарь, содержащий ключ 'metric_info_list' и соответствующее значение.

        Raises:
            MyException527_db: Если запись не найдена
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT metric_info_list FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            self.conn.commit()
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                raise MyException527_db("Vvk Scheme is not registered!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_full: %s", e)
            raise e

    # __ AGENTS __
    def reg_sch_select_count_agents(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_count_agents = "SELECT number_id FROM reg_sch WHERE type_id = TRUE ORDER BY number_id DESC LIMIT 1;"
            cur.execute(sql_count_agents)
            result = cur.fetchone()

            if result is not None:
                return result[0]
            else:
                return 0
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_count_agents: %s", e)
            raise

    def reg_sch_select_agents_all_json(self) -> list:
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT number_id, agent_reg_id, scheme_revision, original_scheme, scheme, metric_info_list 
                    FROM reg_sch 
                    WHERE type_id = TRUE
                """
            cur.execute(sql_select, )
            results = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            result_dicts = [dict(zip(column_names, row)) for row in results]
            return result_dicts
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_agents_all: %s", e)
            raise e

    def reg_sch_select_metrics_and_items(self, agent_id: int) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_query = (f"SELECT scheme_revision, user_query_interval_revision, "
                         f"jsonb_array_elements(scheme->'metrics')->>'metric_id' AS metric_id, "
                         f"jsonb_array_elements(scheme->'item_id_list')->>'item_id' AS item_id "
                         f"FROM reg_sch "
                         f"WHERE number_id = {agent_id};")
            cur.execute(sql_query)
            result = cur.fetchall()
            self.conn.commit()
            if result:
                scheme_revision = result[0][0]
                user_query_interval_revisions = result[0][1]
                metrics_id = [row[2] for row in result]
                items_id = [row[3] for row in result]
                return scheme_revision, user_query_interval_revisions, metrics_id, items_id
            return None, None, []
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_metrics_ids: %s", e)
            raise e

    def reg_sch_select_agent_scheme(self, agent_id: int) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = f"SELECT scheme_revision, user_query_interval_revision, scheme FROM reg_sch WHERE number_id = {agent_id}"
            cur.execute(sql_select, )
            data = cur.fetchall()
            if data:
                result = {
                    "scheme_revision": data[0][0],
                    "user_query_interval_revision": data[0][1],
                    "scheme": data[0][2],
                }
                return result
            else:
                raise Exception(f"Такой агент {agent_id} не зарегистирована!!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_scheme_all: %s", e)
            raise e

    # !!!!!!!!! Обновлено 04.06
    def reg_sch_select_agent_details(self, agent_id: int) -> tuple:
        """
        SQL-запрос для получения 'scheme_revision' и 'user_query_interval_revision' агента.

        Args:
            agent_id (int): Идентификатор агента, для которого требуется получить 'scheme_revision' и 'user_query_interval_revision'.

        Returns:
            tuple: Кортеж, содержащий 'scheme_revision' и 'user_query_interval_revision'.

        Raises:
            MyException427_db: Если агент с заданным идентификатором не найден
            Exception: Если произошла ошибка при выполнении запроса.

        """
        try:
            cur = self.conn.cursor()
            sql_select = f"SELECT scheme_revision, user_query_interval_revision FROM reg_sch WHERE number_id = {agent_id}"
            cur.execute(sql_select, )
            data = cur.fetchall()
            if data:
                return data[0][0], data[0][1]
            else:
                raise MyException427_db(f"This agent '{agent_id}' is not registered!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_agent_details: %s", e)
            raise e

    def reg_sch_select_agent_all(self, agent_id: int) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = f"SELECT agent_reg_id, scheme_revision, metric_info_list FROM reg_sch WHERE number_id = {agent_id}"
            cur.execute(sql_select, )
            result = cur.fetchone()
            if result:
                return result
            else:
                raise Exception(f"Такой агент {agent_id} не зарегистирована!!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_scheme_all: %s", e)
            raise e

    def reg_sch_select_templates_excluding_agent(self, agent_id: int) -> list:
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT DISTINCT jsonb_array_elements(original_scheme->'templates')->>'template_id' AS template_id
                    FROM reg_sch
                    WHERE number_id != %s
                """
            cur.execute(sql_select, (agent_id,))
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return []
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_templates_excluding_agent: %s", e)
            raise e

    def reg_sch_select_metrics_excluding_agent(self, agent_id: int) -> list:
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT DISTINCT jsonb_array_elements(original_scheme->'metrics')->>'metric_id' AS metric_id
                    FROM reg_sch
                    WHERE number_id != %s
                """
            cur.execute(sql_select, (agent_id,))
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return []
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_metrics_excluding_agent: %s", e)
            raise e

    def reg_sch_select_full_paths_agent(self, agent_id: int) -> list:
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT jsonb_array_elements(scheme->'item_id_list')->>'full_path' AS full_paths
                    FROM reg_sch
                    WHERE number_id = %s
                """
            cur.execute(sql_select, (agent_id,))
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return []
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_full_paths_agent: %s", e)
            raise e

    # __ Insert __
    def reg_sch_insert_vvk(self, scheme_revision: int, original_scheme: dict, scheme: dict,
                           metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_insert_scheme = (
                "INSERT INTO reg_sch (type_id, number_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list) "
                "VALUES (FALSE, 0, %s, %s, %s, %s, %s);")
            cur.execute(sql_insert_scheme, (
            scheme_revision, 0, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list)))
            self.conn.commit()
            logger.info("DB(reg_sch): VvkScheme зарегистрирована")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_insert_vvk: %s", e)
            raise e

    def reg_sch_insert_agent(self, number_id: int, agent_reg_id: str, scheme_revision: int,
                             user_query_interval_revision: int, original_scheme: dict, scheme: dict,
                             metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_insert = (
                "INSERT INTO reg_sch (type_id, number_id, agent_reg_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, metric_info_list) "
                "VALUES (TRUE, %s, %s, %s, %s, %s, %s, %s);")
            cur.execute(sql_insert, (
            number_id, agent_reg_id, scheme_revision, user_query_interval_revision, json.dumps(original_scheme),
            json.dumps(scheme), json.dumps(metric_info_list)))
            self.conn.commit()
            logger.info(f"DB(reg_sch): Agent '{number_id}' зарегистрирован")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_insert_agent '%s': %s", number_id, e)
            raise e

    # __ Update __
    def reg_sch_update_vvk_scheme(self, scheme_revision: int, scheme: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update_scheme = "UPDATE reg_sch SET scheme_revision = %s, scheme = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_scheme, (scheme_revision, json.dumps(scheme),))
            logger.info("DB(reg_sch): VvkScheme-scheme изменена")
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_vvk_scheme: %s", e)
            raise e

    def reg_sch_update_vvk_scheme_all(self, scheme_revision: int, original_scheme: dict, scheme: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update_scheme = "UPDATE reg_sch SET scheme_revision = %s, original_scheme = %s, scheme = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_scheme, (scheme_revision, json.dumps(original_scheme), json.dumps(scheme),))
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

    def reg_sch_update_agent_re_reg(self, number_id: int, scheme_revision: int, user_query_interval_revision: int,
                                    original_scheme: dict, scheme: dict, metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE reg_sch SET scheme_revision = %s, user_query_interval_revision = %s, original_scheme = %s, scheme = %s, metric_info_list = %s WHERE number_id = {number_id}"
            cur.execute(sql_update, (
            scheme_revision, user_query_interval_revision, json.dumps(original_scheme), json.dumps(scheme),
            json.dumps(metric_info_list),))
            self.conn.commit()
            logger.info(f"DB(reg_sch): Agent '{number_id}' перезарегистрирована")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_scg_update_agent '%s': %s", number_id, e)
            raise e

    # __ Delete __
    def reg_sch_delete_agent(self, agent_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete = f"DELETE FROM reg_sch WHERE number_id = {agent_id};"
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info(f"DB(reg_sch): удален агент {agent_id}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_delete_agent: %s", e)
            raise e

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