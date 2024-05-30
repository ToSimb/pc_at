import datetime

from logger.logger import logger


class Gui:
    def __init__(self, conn):
        self.conn = conn

# ______________ GUI _______________

# __ Create Table __
    def gui_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS gui (
                    id SERIAL PRIMARY KEY,
                    vvk_name VARCHAR(50),
                    type_id BOOLEAN DEFAULT TRUE,
                    number_id INT,
                    agent_reg_id VARCHAR(30),
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    status_reg BOOLEAN,
                    time_reg TIMESTAMP,
                    error_reg VARCHAR(250),
                    time_value TIMESTAMP,
                    error_value VARCHAR(250),
                    time_conn TIMESTAMP
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(gui): таблица создана")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_create_table: %s", e)
            raise e

# __ Drop Table __
    def gui_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS gui;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(gui): таблица удалена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_drop_table: %s", e)
            raise e

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
            self.conn.rollback()
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
            self.conn.rollback()
            logger.error("DB(gui): gui_select_check_agent_reg_id: %s", e)
            raise e

    def gui_select_check_agent_status_reg(self, number_id: int) -> int:
        try:
            cur = self.conn.cursor()
            sql_select_check = "SELECT status_reg FROM gui WHERE number_id = %s;"
            cur.execute(sql_select_check, (number_id,))
            result = cur.fetchone()
            self.conn.commit()
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_select_check_agent_status_reg: %s", e)
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
            self.conn.rollback()
            logger.error("DB(gui): gui_insert_join_scheme: %s", e)
            raise e

    def gui_insert_agents(self, agent_reg_id: list):
        try:
            cur = self.conn.cursor()
            sql_insert = "INSERT INTO gui (agent_reg_id) VALUES (%s);"
            cur.executemany(sql_insert, [(agent_id,) for agent_id in agent_reg_id])
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_insert_agents: %s", e)
            raise e


# __ Update __
    def gui_update_agent_reg_id_error(self, agent_reg_id: str, status_reg: bool, error_reg: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET status_reg = %s, time_reg = %s, error_reg = %s WHERE agent_reg_id = %s;"
            cur.execute(sql_update_gui, (status_reg, time_reg, error_reg, agent_reg_id))
            self.conn.commit()
            logger.error(f"DB(gui):  agent_reg_id '{agent_reg_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_reg_id_error - agent_reg_id %s : %s", agent_reg_id, e)
            raise e

    def gui_update_agent_id_error(self, agent_id: int, status_reg: bool, error_reg: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET status_reg = %s, time_reg = %s, error_reg = %s WHERE number_id = %s;"
            cur.execute(sql_update_gui, (status_reg, time_reg, error_reg, agent_id))
            self.conn.commit()
            logger.error(f"DB(gui): agent_id '{agent_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_id_error - agent_id %s : %s", agent_id, e)
            raise e

    def gui_update_agent_reg_id_reg(self, agent_id: int, agent_reg_id: str, scheme_revision: int, status_reg: bool, error_reg: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET number_id = %s, scheme_revision = %s, status_reg = %s, time_reg = %s, error_reg = %s WHERE agent_reg_id = %s;"
            cur.execute(sql_update_gui, (agent_id, scheme_revision, status_reg, time_reg, error_reg, agent_reg_id))
            self.conn.commit()
            logger.info(f"DB(gui): agent_reg_id '{agent_reg_id}' статус изменен: {status_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_reg_id_reg - agent_reg_id %s : %s", agent_reg_id, e)
            raise e

    def gui_update_agent_id_reg(self, agent_id: int, scheme_revision: int, status_reg: bool) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET scheme_revision = %s, status_reg = %s, time_reg = %s WHERE number_id = %s;"
            cur.execute(sql_update_gui, (scheme_revision, status_reg, time_reg,  agent_id))
            self.conn.commit()
            logger.info(f"DB(gui): agent_id '{agent_id}' статус изменен: {status_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_id_reg - agent_id %s : %s", agent_id, e)
            raise e

    def gui_update_vvk_reg_error(self,  status_reg: bool, error_reg: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET status_reg = %s, time_reg = %s, error_reg = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_gui, (status_reg, time_reg, error_reg))
            self.conn.commit()
            logger.error(f"DB(gui): ошибка регистрации ВВК: {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_vvk_reg_error: %s", e)
            raise e

    def gui_update_vvk_reg(self, vvk_id: int, scheme_revision: int, user_query_interval_revision: int, status_reg: bool) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET number_id = %s, scheme_revision = %s, user_query_interval_revision = %s, status_reg = %s, time_reg = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_gui,
                        (vvk_id, scheme_revision, user_query_interval_revision, status_reg, time_reg))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_vvk_reg - vvk_id %s : %s", vvk_id, e)
            raise e

    def gui_update_vvk_reg_none(self, scheme_revision: int, user_query_interval_revision: int) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET scheme_revision = %s, user_query_interval_revision = %s, status_reg = NULL WHERE type_id = FALSE;"
            cur.execute(sql_update_gui,
                        (scheme_revision, user_query_interval_revision))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_vvk_reg_none: %s", e)
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
            self.conn.rollback()
            logger.error("DB(gui): gui_delete: %s", e)
            raise e

    def gui_delete_agents(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete = "DELETE FROM gui WHERE type_id = TRUE;"
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info("DB(gui): таблица очищена для строк с type_id = TRUE")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_delete_agents: %s", e)
            raise e