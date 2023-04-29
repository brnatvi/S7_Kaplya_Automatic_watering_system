# Module Imports
import mariadb
import sys

try:
    conn = mariadb.connect(
        user="admin",
        password="admin",
        host="localhost",
        database="arrosage"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()
cur.execute(
    "SELECT name, id_flowerpot " +
    "FROM Plant JOIN Flowerpot on Plant.id_plant=Flowerpot.id_plant")

for (name, id_flowerpot) in cur:
    print(f"Name: {name}, id_flowerpot: {id_flowerpot}")