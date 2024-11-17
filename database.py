import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="01617277318",
    database="test"
)

def save(query, data):
    cur = db.cursor(buffered=True)
    cur.execute(query, data)
    db.commit()
    cur.close()
    return True
