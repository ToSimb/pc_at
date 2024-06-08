from .classes.db_gui import Gui
from .classes.db_reg_sch import Reg_sch
from .classes.db_sch_ver import Sch_ver
from .classes.db_pf import Pf


class Database(Gui, Reg_sch, Sch_ver, Pf):
    def __init__(self, conn):
        self.conn = conn