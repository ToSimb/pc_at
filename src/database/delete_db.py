from database import Database
import datetime

current_datetime = datetime.datetime.now()


one_day_ago_datetime = current_datetime - datetime.timedelta(days=1)

current_timestamp = int(current_datetime.timestamp())
one_day_ago_timestamp = int(one_day_ago_datetime.timestamp())

print("Текущее время - int:", current_timestamp)
print("Время ровно сутки назад - int:", one_day_ago_timestamp)

db = Database()

db.connect()

db.delete_params(one_day_ago_timestamp)

db.disconnect()