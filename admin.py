from werkzeug.security import generate_password_hash

import getpass

import database

while True:
    user_name = input("Username: ")
    email = input("Email: ")

    if not user_name or not email:
        print("Please fill all the required filds")
        continue

    user_list = database.get("SELECT * FROM users WHERE user_name = %s OR email = %s", (user_name, email))

    if len(user_list) > 0:
        print("Usarname taken or email email allraedy in use")
        continue

    break 

while True:
    password = getpass.getpass("Password: ")
    password_again = getpass.getpass("Password (again): ")

    if password == password_again:
        break

    elif not password or not password_again:
        print("Please fill all the required filds")
    
    else:
        print("Confirmation password does not match, pls try again")

database.save("INSERT INTO users (user_name, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)", (user_name, email, generate_password_hash(password), True))
