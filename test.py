import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="01617277318",
    database="test"
)

cur = db.cursor(buffered=True)
cur.execute("SELECT * FROM users WHERE user_name = %s or email = %s", ("Zafir", ""))
# [() , ()]

list_of_tuple = cur.fetchall()
print(len(list_of_tuple))
