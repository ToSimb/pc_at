from database.postgres import connect, disconnect
from database.pf import Pf
from database.gui import Gui
from database.reg_sch import Reg_sch
from database.sch_ver import Sch_ver

conn = connect()

db_gui = Gui(conn)
db_gui.gui_drop_table()
db_gui.gui_create_table()

db_reg = Reg_sch(conn)
db_reg.reg_sch_drop_table()
db_reg.reg_sch_create_table()

db_sch = Sch_ver(conn)
db_sch.sch_ver_drop_table()
db_sch.sch_ver_create_table()

db_pf = Pf(conn)
db_pf.pf_drop_table()
db_pf.pf_create_table()


disconnect(conn)