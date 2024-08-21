from database.postgres import connect, disconnect
from database.db import Database


try:
    conn = connect()

    db = Database(conn)

    db.pf_delete_params()

    disconnect(conn)
except Exception as e:
    print(e)