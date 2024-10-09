from database.postgres import connect, disconnect
from database.db import Database


try:
    conn = connect()

    db = Database(conn)

    db.pf_drop_table()
    db.pf_create_table()

    db.flag_drop_table()
    db.flag_create_table()
    db.flag_insert()

    disconnect(conn)
except Exception as e:
    print(e)