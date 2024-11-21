import database
import datetime

print(database.get("SELECT * FROM test", ())[0][1])
print(datetime.datetime(2024, 11, 21, 12, 23, 55))
