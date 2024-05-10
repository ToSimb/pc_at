import json

from logger.logger import logger

class Reg_sch:
    def __init__(self, conn):
        self.conn = conn

# ____________ REG_SCH _____________
    def reg_sch_create_table(self):
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS reg_sch (
                    id SERIAL PRIMARY KEY,
                    type_id BOOLEAN,
                    number_id INT,
                    agent_reg_id VARCHAR(20),
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    scheme JSONB,
                    item_id_list JSONB[],
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

    def reg_sch_drop_table(self):
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

    def reg_sch_execute_join_scheme(self, scheme_revision: int, scheme: dict):
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
