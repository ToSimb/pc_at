import json

from logger.logger import logger

class Reg_sch:
    def __init__(self, conn):
        self.conn = conn

# ____________ REG_SCH _____________
    def reg_sch_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS reg_sch (
                    id SERIAL PRIMARY KEY,
                    type_id BOOLEAN,
                    number_id INT,
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    original_scheme JSONB,
                    scheme JSONB,
                    metric_info_list JSONB,
                    block BOOLEAN DEFAULT FALSE
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(reg_sch): таблица создана")
            return True
        except Exception as e:
            logger.error("DB(reg_sch): ошибка создания таблицы: %s", e)
            raise e
    def reg_sch_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS reg_sch;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(reg_sch): таблица удалена")
            return True
        except Exception as e:
            logger.error("DB(reg_sch): ошибка удаления таблицы: %s", e)
            raise e
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
                sql_insert_scheme = ("INSERT INTO reg_sch (type_id, scheme_revision, original_scheme, scheme, metric_info_list) "
                                     "VALUES (FALSE, %s, %s, %s, %s);")
                cur.execute(sql_insert_scheme, (scheme_revision, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list)))
                self.conn.commit()
                logger.info("DB(reg_sch): VvkScheme зарегистрирована")
            return True
        except Exception as e:
            logger.error("DB(reg_sch): ошибка регистрации VvkScheme: %s", e)
            raise e
    def reg_sch_select_vvk_schemes(self) -> tuple:
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT original_scheme, scheme, metric_info_list FROM reg_sch WHERE type_id = FALSE"
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
    def reg_sch_update_vvk_scheme(self, scheme: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update_scheme = "UPDATE reg_sch SET scheme = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_scheme, (json.dumps(scheme),))
            logger.info("DB(reg_sch): VvkScheme-scheme изменена")
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("DB(reg_sch): ошибка при изменении VvkScheme-scheme: %s", e)
            raise e


    def reg_sch_registration_agent(self, number_id: int, scheme_revision: int, original_scheme: dict, scheme: dict, metric_info_list: dict) -> bool:
        try:
            cur = self.conn.cursor()
            sql_check_existence = f"SELECT COUNT(*) FROM reg_sch WHERE number_id = {number_id};"
            cur.execute(sql_check_existence)
            count = cur.fetchone()[0]
            self.conn.commit()
            if count > 0:
                sql_update = f"UPDATE reg_sch SET scheme_revision = %s, original_scheme = %s, scheme = %s, metric_info_list = %s WHERE number_id = {number_id}"
                cur.execute(sql_update, (scheme_revision, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list),))
                self.conn.commit()
                logger.info(f"DB(reg_sch): Agent '{number_id}' перезарегистрирована")
            else:
                sql_insert = ("INSERT INTO reg_sch (type_id, number_id, scheme_revision, original_scheme, scheme, metric_info_list) "
                                     "VALUES (TRUE, %s, %s, %s, %s, %s);")
                cur.execute(sql_insert, (number_id, scheme_revision, json.dumps(original_scheme), json.dumps(scheme), json.dumps(metric_info_list)))
                self.conn.commit()
                logger.info(f"DB(reg_sch): Agent '{number_id}' зарегистрирована")
            return True
        except Exception as e:
            logger.error("DB(reg_sch): ошибка регистрации agenta '%s': %s", number_id, e)
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
            raise

    def reg_sch_block_true(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_update = "UPDATE reg_sch SET block = TRUE WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение block успешно изменено на True")
            return True
        except Exception as e:
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







    def reg_sch_get_metrics_ids(self) -> list:
        # переписать. так задел на будущее
        try:
            cur = self.conn.cursor()
            sql_query = "SELECT jsonb_array_elements(scheme->'metrics')->>'id' AS ids FROM reg_sch;"
            cur.execute(sql_query)
            result = cur.fetchall()
            metrics_ids = [row[0] for row in result]
            return metrics_ids
        except Exception as e:
            logger.error("DB(reg_sch): ошибка получения идентификаторов метрик: %s", e)
            raise e