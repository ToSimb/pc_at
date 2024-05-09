import psycopg2

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
from logger.logger import logger

def connect():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        logger.info("Успешное подключение к БД")
        return conn
    except Exception as e:
        logger.info("Ошибка при подключении к БД:", e)


def disconnect(conn):
    if conn is not None:
        conn.close()
        logger.info("Соединение с БД закрыто")
