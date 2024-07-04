from database.postgres import connect, disconnect
from database.db import Database


def reg_sch_select_agent_details(conn,  agent_id: int) -> tuple:
    try:
        cur = conn.cursor()
        sql_select = f"SELECT  scheme_revision, original_scheme, scheme FROM reg_sch WHERE number_id = {agent_id}"
        cur.execute(sql_select, )
        data = cur.fetchone()
        conn.commit()
        if data:
            return data
        else:
            print(f"This agent '{agent_id}' is not registered!")
    except Exception as e:
        print("DB(reg_sch): reg_sch_select_agent_details: %s", e)
        raise e

try:
    conn = connect()

    a = reg_sch_select_agent_details(conn, 1)
    print(a[0])
    print("________________")
    print(a[1])
    print("________________")
    print(a[2])

    disconnect(conn)
except Exception as e:
    print(e)