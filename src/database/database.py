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
    def __init__(self):
        self.dbname = DB_NAME
        self.user = DB_USER
        self.password = DB_PASS
        self.host = DB_HOST
        self.port = DB_PORT
        self.conn = None


    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Успешное подключение к БД")
        except Exception as e:
            print("Ошибка при подключении к БД:", e)


    def disconnect(self):
        if self.conn is not None:
            self.conn.close()
            print("Соединение с БД закрыто") 
    

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
            cur = self.conn.cursor()
            sql_insert_data = " INSERT INTO test (scheme_revision, user_query_interval_revision, item_id, metric_id, t, v, etmax, etmin, comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            cur.execute(sql_insert_data, (scheme_revision, user_query_interval_revision, item_id, metric_id, t, v, etmax, etmin, comment))
            self.conn.commit()
        except Exception as e:
            print("Ошибка БД - не удалось сделать execute_params:", e)
            return None


    def select_data(self):
        try:
            cur = self.conn.cursor()
            sql_select_data = "SELECT * FROM test;"
            cur.execute(sql_select_data)
            data = cur.fetchall()
            return data
        except Exception as e:
            print("Ошибка при чтении данных из таблицы:", e)
            return None