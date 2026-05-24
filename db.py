import os
import mysql.connector
from mysql.connector import Error

def get_connection():
    """Return a MySQL connection.
    On Railway: reads MYSQLHOST, MYSQLUSER, MYSQLPASSWORD, MYSQLPORT, MYSQL_DATABASE
    Locally: falls back to localhost/bus_reservation
    """
    try:
        conn = mysql.connector.connect(
            host     = os.environ.get("MYSQLHOST",     "localhost"),
            port     = int(os.environ.get("MYSQLPORT", 3306)),
            user     = os.environ.get("MYSQLUSER",     "root"),
            password = os.environ.get("MYSQLPASSWORD", "your_password"),
            database = os.environ.get("MYSQL_DATABASE", os.environ.get("DB_NAME", "bus_reservation")),
        )
        return conn
    except Error as e:
        raise ConnectionError(f"Could not connect to MySQL: {e}")
