import sys
print("test")
import mysql.connector

print("test")

try:
    conn = mysql.connector.connect(
        user="admin",
        password="angel200399",
        host="localhost",
        port=3306,
        database="arrosage"
    )
except mysql.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

for param in sys.argv:
    print (param)