from database import Database

db = Database()

db.connect()

print (db.select_data())

db.disconnect()