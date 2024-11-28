import mysql.connector

import key

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = key.get_database_password(),
    database = "test"
)

def save(query, data):
    cur = db.cursor(buffered=True)

    cur.execute(query, data)

    db.commit()

    cur.close()

    return True


def get(query, data):
    cur = db.cursor(buffered=True, dictionary=True)

    cur.execute(query, data)
    
    return cur.fetchall()
