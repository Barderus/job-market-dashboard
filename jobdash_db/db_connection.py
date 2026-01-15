import os
import mysql.connector
from mysql.connector import errorcode

from dotenv import load_dotenv
load_dotenv()

def get_connection():
    try:
        connection = mysql.connector.connect(
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            database=os.getenv("MYSQL_DB"),
            autocommit=True
        )
        return connection


    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise RuntimeError("Invalid MySQL credentials")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise RuntimeError("Database does not exist")
        else:
            raise RuntimeError(f"MySQL connection failed: {err}")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT DATABASE();")
print(cursor.fetchone())

cursor.close()
conn.close()