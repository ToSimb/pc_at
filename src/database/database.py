from logger.logger import logger


class Database:
    def __init__(self, conn):
        self.conn = conn

# ______________ GUI _______________



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
