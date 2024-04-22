import os

from dotenv import load_dotenv

import psycopg2

#from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")


def connect():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Успешное подключение к БД")
        return conn
    except Exception as e:
        print("Ошибка при подключении к БД:", e)

def disconnect(conn):
    if conn is not None:
        conn.close()
        print("Соединение с БД закрыто") 
