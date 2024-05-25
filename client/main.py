import json

from database.postgres import connect, disconnect
from database.pf import Pf
from database.gui import Gui
from database.reg_sch import Reg_sch
from database.sch_ver import Sch_ver

conn = connect()


def delete_metrics(vvk_scheme_metrics_list: dict, list_metrics: list):
    print("metrics", len(list_metrics))
    metrics_list = []
    for item in vvk_scheme_metrics_list:
        if item["metric_id"] in list_metrics:
            metrics_list.append(item)
    return metrics_list

def delete_templates(vvk_scheme_templates_list: list, list_templates: list):
    print("templates", len(list_templates))
    templates_list = []
    for item in vvk_scheme_templates_list:
        if item["template_id"] in list_templates:
            templates_list.append(item)
    return templates_list

# GUI
db_gui = Gui(conn)


# REG_SCH
db_reg = Reg_sch(conn)

scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, metric_info_list = db_reg.reg_sch_select_vvk_all()

agent_id = 1
# очистка
metrics_list_excluding_agent = db_reg.reg_sch_select_metrics_excluding_agent(agent_id)
templates_list_excluding_agent = db_reg.reg_sch_select_templates_excluding_agent(agent_id)


templates_new = delete_templates(vvk_scheme["templates"], templates_list_excluding_agent)
print("templates_new:", len(templates_new))
metrics_new = delete_metrics(vvk_scheme["metrics"], metrics_list_excluding_agent)
print("metrics_new:", len(metrics_new))


# SCH_VER
db_sch = Sch_ver(conn)



disconnect(conn)