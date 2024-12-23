import mysql.connector

import key

ssl_ca = "/ca.pem"

db = mysql.connector.connect(
    host = "b2b-zafirchowdhury69-c101.j.aivencloud.com",
    port = 10728,
    user = "avnadmin",
    password = key.get_database_password(),
    database = "b2b",
    ssl_ca=ssl_ca
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
