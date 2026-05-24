import os
import mysql.connector
from mysql.connector import Error

def get_connection():
    """Return a MySQL connection.
    Reads Railway's native variable names (MYSQLHOST, MYSQLUSER, etc.)
    Falls back to local defaults for development.
    """
    try:
        conn = mysql.connector.connect(
            host     = os.environ.get("MYSQLHOST",     "localhost"),
            port     = int(os.environ.get("MYSQLPORT", 3306)),
            user     = os.environ.get("MYSQLUSER",     "root"),
            password = os.environ.get("MYSQLPASSWORD", "your_password"),  # change for local
            database = os.environ.get("MYSQL_DATABASE","bus_reservation"),
        )
        return conn
    except Error as e:
        raise ConnectionError(f"Could not connect to MySQL: {e}")
