import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def connect_to_database():
    return pymysql.connect(
        host='localhost',
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor
    )