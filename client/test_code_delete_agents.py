import json
import sys
import subprocess

from database.postgres import connect, disconnect
from database.pf import Pf
from database.gui import Gui
from database.reg_sch import Reg_sch
from database.sch_ver import Sch_ver


def delete_metrics(vvk_scheme_metrics_list: dict, list_metrics: list):
    metrics_list = [item for item in vvk_scheme_metrics_list if item["metric_id"] in list_metrics]
    return metrics_list

def delete_templates(vvk_scheme_templates_list: list, list_templates: list):
    templates_list = [item for item in vvk_scheme_templates_list if item["template_id"] in list_templates]
    return templates_list

def delete_item_id_list(vvk_scheme_item_id_list: list, full_paths_agent: list):
    item_id_list = [item for item in vvk_scheme_item_id_list if item['full_path'] not in full_paths_agent]
    return item_id_list

def delete_item_info_list(vvk_scheme_item_info_list: list, join_scheme_item_info_list: list, full_paths_agent: list):
    item_info_list = [item for item in vvk_scheme_item_info_list if item['full_path'] not in full_paths_agent]
    item_info_list.extend(item for item in join_scheme_item_info_list if item['full_path'] in full_paths_agent)
    return item_info_list

try:
    conn = connect()

    # ОЧИСТКА БД
    subprocess.run(['python', 'create_table.py'])
    # РЕГИСТРАЦИЯ JOIN
    subprocess.run(['python', 'test_reg_join_scheme.py'])
    # РЕГИСТРАЦИЯ AGENTS
    subprocess.run(['python', 'test_reg_agents.py'])

    print(" __ РАБОТАЕМ __")
    agent_id = 2

    print("Agent:", agent_id)

    # GUI
    db_gui = Gui(conn)


    # REG_SCH
    db_reg = Reg_sch(conn)

    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, metric_info_list = db_reg.reg_sch_select_vvk_all()
    #

    # очистка метрик и шаблонов

    # получение данных с помощью которых будет произоводиться очистка
    metrics_list_excluding_agent = db_reg.reg_sch_select_metrics_excluding_agent(agent_id)
    templates_list_excluding_agent = db_reg.reg_sch_select_templates_excluding_agent(agent_id)
    full_paths_agent = db_reg.reg_sch_select_full_paths_agent(agent_id)


    templates_new = delete_templates(vvk_scheme["templates"], templates_list_excluding_agent)
    metrics_new = delete_metrics(vvk_scheme["metrics"], metrics_list_excluding_agent)
    item_id_list_new = delete_item_id_list(vvk_scheme["item_id_list"], full_paths_agent)
    item_info_list_new = delete_item_info_list(vvk_scheme['item_info_list'], join_scheme['item_info_list'], full_paths_agent)

    vvk_scheme_after_cleaning = {
        "metrics": metrics_new,
        "templates": templates_new,
        "item_id_list": item_id_list_new,
        "item_info_list": item_info_list_new,
    }

    print(vvk_scheme_after_cleaning)

    # SCH_VER
    db_sch = Sch_ver(conn)



    disconnect(conn)
except:
    sys.exit(1)
    disconnect(conn)