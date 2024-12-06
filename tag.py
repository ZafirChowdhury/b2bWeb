import mysql.connector

import key

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = key.get_database_password(),
    database = "test"
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
