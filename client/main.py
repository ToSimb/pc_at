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
json_scheme = json.loads(data)

# GUI
db_gui = Gui(conn)


# REG_SCH
db_reg = Reg_sch(conn)

print (db_reg.reg_sch_select_vvk_scheme())
# SCH_VER
db_sch = Sch_ver(conn)



disconnect(conn)