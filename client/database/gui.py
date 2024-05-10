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
                    error_reg VARCHAR(100),
                    time_conn TIMESTAMP,
                    time_value TIMESTAMP
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
            logger.info("DB(gui): таблица очищена>")
            return True
        except Exception as e:
            logger.error("DB(gui): ошибка удаления строк: %s", e)
            raise e

    def gui_execute_join_scheme(self, vvk_name: str, agent_reg_id: list):
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

    def gui_drop_table(self):
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