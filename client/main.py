import json

from database.postgres import connect, disconnect
from database.pf import Pf
from database.gui import Gui
from database.reg_sch import Reg_sch
from database.sch_ver import Sch_ver

conn = connect()

def create_vvk_scheme(join_scheme):
    # Формируем структуру VvkScheme
    scheme = {
            "metrics": [],
            "templates": join_scheme["templates"],
            "item_id_list": [],
            "item_info_list": join_scheme["item_info_list"]
    }
    # Создаем пустой список и индекс для формирования item_id_list
    item_id_list = []
    index = 0
    # формирования списка с item_id_list
    for a in join_scheme["item_id_list"]:
        item_id_list.append({"full_path": a["full_path"], "item_id": index})
        index += 1
    # Добавление item_id_list в json
    scheme["item_id_list"] = item_id_list
    return scheme



with open("json/JoinScheme.json", 'r', encoding='utf-8') as file:
    data = file.read()
# Преобразование JSON в словарь
json_data = json.loads(data)


# GUI
db_gui = Gui(conn)
db_gui.gui_drop_table()
db_gui.gui_create_table()
# 1 - vvk_name
vvk_puth = json_data["scheme"]["item_id_list"][0]["full_path"].split("/")[0]
vvk_name = [item for item in json_data["scheme"]["templates"] if item.get('template_id') == vvk_puth][0]["name"]
# 2 - list agent_reg_id
agent_reg_id = [item["agent_reg_id"] for item in json_data["scheme"]["join_list"]]
db_gui.gui_registration_join_scheme(vvk_name, agent_reg_id)


# REG
db_reg = Reg_sch(conn)
db_reg.reg_sch_drop_table()
db_reg.reg_sch_create_table()

a = create_vvk_scheme(json_data["scheme"])
db_reg.reg_sch_registration_vvk_scheme(json_data['scheme_revision'], json_data["scheme"], a, {})
db_reg.reg_sch_registration_agent(1,0,{},{},None)



# b, c, d = db_reg.reg_sch_select_vvk_schemes()
# print (b['join_list'])
# print (c)
# print (d)

# print(db_reg.reg_sch_check_block())
# print( db_reg.reg_sch_count_agents())


# SCH
#
# db_sch = Sch_ver(conn)
# db_sch.sch_ver_drop_table()
# db_sch.sch_ver_create_table()



# остальное


disconnect(conn)