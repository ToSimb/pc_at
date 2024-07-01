from logger.logger import logger
from database.classes.gui import Gui
from database.classes.reg_sch import Reg_sch
from database.classes.sch_ver import Sch_ver
from database.classes.pf import Pf
from database.classes.flag import Flag

class Database(Gui, Reg_sch, Sch_ver, Pf, Flag):
    def __init__(self, conn):
        self.conn = conn


    def select_last_agents_reg(self, name_table: str) -> list:
        try:
            cur = self.conn.cursor()
            sql_select_last_50_agents_reg_id = f"SELECT * FROM {name_table} ORDER BY id DESC;"
            cur.execute(sql_select_last_50_agents_reg_id)
            rows = cur.fetchall()
            self.conn.commit()
            columns = [desc[0] for desc in cur.description]
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            logger.error("общая DB: ошибка получения последних строк: %s", e)
            raise e