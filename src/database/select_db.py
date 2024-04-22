from database import Database

db = Database()

db.connect()

print (db.select_params())

print ("________________________")

for i in db.select_params_json():
    print (i)

db.disconnect()