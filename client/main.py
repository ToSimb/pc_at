from database.postgres import connect, disconnect
from database.pf import Pf


conn = connect()

db = Pf(conn)


print(db.pf_select_params_json())

disconnect(conn)