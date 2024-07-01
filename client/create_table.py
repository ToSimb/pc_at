from database.postgres import connect, disconnect
from database.db import Database


try:
    conn = connect()

    db = Database(conn)

    db.gui_drop_table()
    db.gui_create_table()

    db.reg_sch_drop_table()
    db.reg_sch_create_table()

    db.sch_ver_drop_table()
    db.sch_ver_create_table()

    db.pf_drop_table()
    db.pf_create_table()

    db.flag_drop_table()
    db.flag_create_table()
    db.flag_insert()

    disconnect(conn)
except Exception as e:
    print(e)