import database 

user_list =  database.get("SELECT * FROM users WHERE user_name = %s or email = %s", ("Labiba", "Labiba"))
print(user_list)
