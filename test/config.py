import os

from dotenv import load_dotenv

load_dotenv()

MY_PORT = os.environ.get('MY_PORT')

PC_AF_PROTOCOL = os.environ.get("PC_AF_PROTOCOL")
PC_AF_IP = os.environ.get("PC_AF_IP")
PC_AF_PORT = os.environ.get("PC_AF_PORT")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

PF_LIMIT = os.environ.get("PF_LIMIT")
T3 = os.environ.get("T3")
DEBUG = os.environ.get("DEBUG")