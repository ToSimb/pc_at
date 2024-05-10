import json

from database.postgres import connect, disconnect
from database.pf import Pf
from database.gui import Gui
from database.reg_sch import Reg_sch
from database.sch_ver import Sch_ver




conn = connect()





# with open("json/JoinScheme.json", 'r', encoding='utf-8') as file:
#     data = file.read()
#
# # Преобразование JSON в словарь
# json_data = json.loads(data)
#
db = Gui(conn)
db.gui_drop_table()
db.gui_create_table()
# # 1 - vvk_name
# vvk_puth = json_data["scheme"]["item_id_list"][0]["full_path"].split("/")[0]
# vvk_name = [item for item in json_data["scheme"]["templates"] if item.get('template_id') == vvk_puth][0]["name"]
#
# # 2 - list agent_reg_id
# agent_reg_id = [item["agent_reg_id"] for item in json_data["scheme"]["join_list"]]
#
# db.gui_execute_join_scheme(vvk_name, agent_reg_id)
#
#
#
db_reg = Reg_sch(conn)
db_reg.reg_sch_drop_table()
db_reg.reg_sch_create_table()
# db_reg.reg_sch_execute_join_scheme(json_data["scheme_revision"], json_data["scheme"])
# db_reg.reg_sch_get_metrics_ids()
#
#
#
db_sch = Sch_ver(conn)
db_sch.sch_ver_drop_table()
db_sch.sch_ver_create_table()
#
#
# db.gui_delete()

disconnect(conn)