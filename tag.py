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

cur = db.cursor()

tag_list = [
    "Electronics",
    "Fashion",
    "Home & Garden",
    "Sports & Outdoors",
    "Health & Beauty",
    "Toys & Games",
    "Books",
    "Music",
    "Movies",
    "Automotive",
    "Art & Collectibles",
    "Baby Products",
    "Office Supplies",
    "Pet Supplies",
    "Jewelry",
    "Shoes",
    "Clothing",
    "Furniture",
    "Kitchen Appliances",
    "Gadgets"
]

for tag in tag_list:
    cur.execute("INSERT INTO tags (tag) VALUES (%s)", (tag,))

db.commit()
cur.close()

print("Tags added successfully")
