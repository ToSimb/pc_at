import os

from dotenv import load_dotenv

load_dotenv()

PC_AF_PROTOCOL = os.environ.get("PC_AF_PROTOCOL")
PC_AF_IP = os.environ.get("PC_AF_IP")
PC_AF_PORT = os.environ.get("PC_AF_PORT")
PC_AF_PATH = os.environ.get("PC_AF_PATH")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")