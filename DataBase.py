import mysql.connector
from mysql.connector import Error

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MYSQL123",
            database="Cafeteria"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None
