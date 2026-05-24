import os
import mysql.connector
from mysql.connector import Error

def get_connection():
    """Return a MySQL connection using environment variables."""
    try:
        conn = mysql.connector.connect(
            host     = os.environ.get("DB_HOST",     "localhost"),
            port     = int(os.environ.get("DB_PORT", 3306)),
            user     = os.environ.get("DB_USER",     "root"),
            password = os.environ.get("DB_PASSWORD", "your_password"),  # local fallback
            database = os.environ.get("DB_NAME",     "bus_reservation"),
        )
        return conn
    except Error as e:
        raise ConnectionError(f"Could not connect to MySQL: {e}")
