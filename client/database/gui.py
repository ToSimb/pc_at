import datetime

from logger.logger import logger

class Gui:
    def __init__(self, conn):
        self.conn = conn

# ______________ GUI _______________
    def gui_create_table(self):
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS gui (
                    id SERIAL PRIMARY KEY,
                    vvk_name VARCHAR(50),
                    type_id BOOLEAN DEFAULT TRUE,
                    number_id INT,
                    agent_reg_id VARCHAR(20),
                    status_reg BOOLEAN,
                    time_reg TIMESTAMP,
                    error_reg VARCHAR(200),
                    time_value TIMESTAMP,
                    error_value VARCHAR(200),
                    time_conn TIMESTAMP
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(gui): таблица создана")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка создания таблицы: %s", e)
            raise e
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
    def gui_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS gui;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(gui): таблица удалена")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка удаления таблицы: %s", e)
            raise e

    def gui_registration_join_scheme(self, vvk_name: str, agent_reg_id: list):
        try:
            cur = self.conn.cursor()
            sql_create = "INSERT INTO gui (vvk_name, type_id) VALUES (%s,%s);"
            cur.execute(sql_create, (vvk_name, False))
            sql_create = "INSERT INTO gui (agent_reg_id) VALUES (%s);"
            cur.executemany(sql_create, [(agent_id,) for agent_id in agent_reg_id])
            self.conn.commit()
            logger.info("DB(gui): JoinScheme загружена")
            return True
        except Exception as e:
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
                logger.error(f"DB(gui):  agent_reg_id '{agent_reg_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка регистации agent_reg_id %s : %s", agent_reg_id, e)
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

    def gui_params_reg_value(self, agent_id: int, error_value: str) -> bool:
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_value = %s, error_value = %s WHERE number_id = %s;"
            cur.execute(sql_update_gui, (time_reg, error_value, agent_id))
            self.conn.commit()
            if error_value:
                logger.error(f"DB(gui): ошибка приема ПФ agent_id '{agent_id}': {error_value}")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка работы БД при вызове gui_params_reg_value: %s", e)
            raise e
