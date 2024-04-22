import os

from dotenv import load_dotenv

import psycopg2

#from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

class Database:
    def __init__(self, conn):
        self.conn = conn
    

    def create_table(self):
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS test (
                    id SERIAL PRIMARY KEY,
                    scheme_revision INT NOT NULL,
                    user_query_interval_revision INT NOT NULL,
                    item_id INT NOT NULL,
                    metric_id VARCHAR(100) NOT NULL,
                    t INT NOT NULL,
                    v INT NOT NULL,
                    etmax BOOLEAN,
                    etmin BOOLEAN,
                    comment VARCHAR(100)
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            print("Таблица 'test' создана")
        except Exception as e:
            print("Ошибка при создании таблицы 'test'", e)


    def execute_params(self, 
                       scheme_revision: int, 
                       user_query_interval_revision: int,
                       item_id: int,
                       metric_id: str,
                       t: int,
                       v: int,
                       etmax: bool,
                       etmin: bool,
                       comment: str):
        try:
            with self.conn.cursor() as curs:
                sql_insert_data = " INSERT INTO test (scheme_revision, user_query_interval_revision, item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                curs.execute(sql_insert_data, (scheme_revision, user_query_interval_revision, item_id, metric_id, t, v, etmax, etmin, comment))

        except Exception as e:
            print("Ошибка БД - не удалось сделать execute_params:", e)
            return None


    def delete_params(self, one_day_ago_timestamp: int):
        try:
            cur = self.conn.cursor()
            sql_delete_params = f"DELETE FROM test WHERE t < {one_day_ago_timestamp};"
            cur.execute(sql_delete_params)
            self.conn.commit()
        except Exception as e:
            print("Ошибка БД - не удалось удалить лишние строки:", e)
            return None


    def select_params(self):
        try:
            cur = self.conn.cursor()
            sql_select_params = "SELECT * FROM test;"
            cur.execute(sql_select_params)
            data = cur.fetchall()
            return data
        except Exception as e:
            print("Ошибка при чтении данных из таблицы:", e)
            return None


    def select_params_json(self):
        try:
            cur = self.conn.cursor()
            sql_select_params = "SELECT * FROM test;"
            cur.execute(sql_select_params)
            data = cur.fetchall()

            columns = [desc[0] for desc in cur.description]
            result = []
            for row in data:
                result.append(dict(zip(columns, row)))

            #json_data = json.dumps(result)
            return result

        except Exception as e:
            print("Ошибка при чтении данных из таблицы:", e)
            return None