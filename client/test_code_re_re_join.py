import json
import sys
import subprocess

from database.postgres import connect, disconnect
from database.pf import Pf
from database.gui import Gui
from database.reg_sch import Reg_sch
from database.sch_ver import Sch_ver

def open_json(name_file: str):
    with open(name_file, 'r', encoding='utf-8') as file:
        data = file.read()
    return json.loads(data)

def add_metrics(json_vvk_return_metrics, json_agent_scheme_metrics):
    metrics_list = json_vvk_return_metrics[:]
    for item in json_agent_scheme_metrics:
        existing_metric = next(
            (metric for metric in json_vvk_return_metrics if metric["metric_id"] == item["metric_id"]),
            None)
        if existing_metric:
            if existing_metric != item:
                raise ValueError(
                    "Ошибка: Метрика с идентификатором '{}' уже существует, но имеет различные параметры".format(
                        item["metric_id"]))
        else:
            metrics_list.append(item)
    return metrics_list

def add_templates(json_vvk_return_templates, json_agent_scheme_templates):
    templates_list = json_vvk_return_templates[:]
    for item in json_agent_scheme_templates:
        existing_template = next((template for template in json_vvk_return_templates if
                                  template["template_id"] == item["template_id"]), None)
        if existing_template:
            if existing_template != item:
                raise ValueError(
                    "Ошибка: Шаблон с идентификатором '{}' уже существует, но имеет различные параметры".format(
                        item["template_id"]))
        else:
            templates_list.append(item)
    return templates_list

def check_full_path_exists(item_list, target_path):
    for item in item_list:
        if item['full_path'] == target_path:
            return False
    return True

def formation_agent_update_join(agent_scheme: dict, join_scheme: dict, vvk_scheme: dict):
    for join_list in join_scheme["join_list"]:
        if agent_scheme["agent_reg_id"] == join_list["agent_reg_id"]:
            # если тип подключения jtInclude
            if join_list["join_type"] == "jtInclude":
                try:
                    # проверка и добавление metrics
                    vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent_scheme['scheme']['metrics'])
                    # проверка и добавление templates
                    vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent_scheme['scheme']['templates'])
                except ValueError as e:
                    raise ValueError(e)

                for item in agent_scheme["scheme"]["join_id_list"]:
                    full_path_item = join_list["join_item_full_path"] + '/' + item["full_path"]
                    if check_full_path_exists(join_scheme["item_id_list"], full_path_item):
                        raise ValueError(
                            f"Ошибка: При попытки регистрации агента по типу соединения 'jtInclude' не был найден путь в Jion: {full_path_item}")

                # Формирование нового item_id_list
                for a in agent_scheme["scheme"]["item_id_list"]:
                    for existing_item in vvk_scheme["item_id_list"]:
                        if existing_item["full_path"] == a["full_path"]:
                            existing_item["item_id"] = a["item_id"]
                            break
                    else:
                        vvk_scheme["item_id_list"].append(a)

                # Формирование нового item_info_list
                for a in agent_scheme["scheme"]["item_info_list"]:
                    b = next(
                        (b for b in vvk_scheme["item_info_list"] if
                         b["full_path"] == a["full_path"]),
                        None)
                    if b:
                        b.update(a)
                    else:
                        vvk_scheme["item_info_list"].append(a)

            # если тип подключения jtExclude
            if join_list["join_type"] == "jtAssign":
                # проверка и добавление metrics
                vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent_scheme['scheme']['metrics'])
                # проверка и добавление templates
                vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent_scheme['scheme']['templates'])

                if len(join_list["joins"]) != len(agent_scheme["scheme"]["join_id_list"]):
                    raise ValueError("Ошибка: разное количество join_id_list с JoinSheme")

                # проходимся по join_id_list в json_agent_scheme
                for join_id_list_scheme in join_list["joins"]:
                    join_id_list_agent = next(
                        (join_id_list_agent for join_id_list_agent in agent_scheme["scheme"]["join_id_list"]
                         if join_id_list_scheme["agent_item_join_id"] == join_id_list_agent["join_id"]), None)
                    if join_id_list_agent:
                        # формирование списка item_id_list
                        for a in agent_scheme["scheme"]["item_id_list"]:
                            for existing_item in vvk_scheme["item_id_list"]:
                                if existing_item["full_path"] == a["full_path"]:
                                    existing_item["item_id"] = a["item_id"]
                                    break
                            else:
                                vvk_scheme["item_id_list"].append(a)

                        # формирование списка item_info_list
                        for a in agent_scheme["scheme"]["item_info_list"]:
                            b = next(
                                (b for b in vvk_scheme["item_info_list"] if
                                 b["full_path"] == a["full_path"]),
                                None)
                            if b:
                                b.update(a)
                            else:
                                vvk_scheme["item_info_list"].append(a)

                    else:
                        raise ValueError("Ошибка: нет :{} в join_id_list".format(
                            join_id_list_scheme["agent_item_join_id"]))

    return vvk_scheme


try:
    conn = connect()

    # # ОЧИСТКА БД
    # subprocess.run(['python', 'create_table.py'])
    # # РЕГИСТРАЦИЯ JOIN
    # subprocess.run(['python', 'test_reg_join_scheme.py'])
    # # РЕГИСТРАЦИЯ AGENTS
    # subprocess.run(['python', 'test_reg_agents.py'])

    # GUI
    db_gui = Gui(conn)
    # REG_SCH
    db_reg = Reg_sch(conn)
    # SCH_VER
    db_sch = Sch_ver(conn)

    print(" __ РАБОТАЕМ __")

    # Получаем данные
    join_scheme_new = open_json("json/JoinScheme_new.json")
        # делаем проверку!!!
    scheme_revision_vvk_new = join_scheme_new["scheme_revision"]
    # Формируем структуру VvkSchemeNew:Scheme
    vvk_scheme_new = {
        "metrics": [],
        "templates": join_scheme_new["scheme"]["templates"],
        "item_id_list": [],
        "item_info_list": join_scheme_new["scheme"]["item_info_list"]
    }
    item_id_list = []
    index = 0
    for a in join_scheme_new["scheme"]["item_id_list"]:
        item_id_list.append({"full_path": a["full_path"], "item_id": index})
        index += 1
    vvk_scheme_new["item_id_list"] = item_id_list

    # GUI
    db_gui.gui_delete_agents()
    agent_reg_id_new = [item["agent_reg_id"] for item in join_scheme_new["scheme"]["join_list"]]
    db_gui.gui_insert_agents(agent_reg_id_new)

    # получаем схемы комплекса
    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, metric_info_list = db_reg.reg_sch_select_vvk_all()
    with open('Orginal.json', 'w') as json_file:
        json.dump(vvk_scheme, json_file, indent=4, ensure_ascii=False)
    # print("original len metrics", len(vvk_scheme["metrics"]))
    # print("original len templates", len(vvk_scheme["templates"]))
    # print("original len item_id_list", len(vvk_scheme["item_id_list"]))
    # print("original len item_info_list", len(vvk_scheme["item_info_list"]))

    # получаем схемы агентов
    agents_all_list = db_reg.reg_sch_select_agents_all_json()
    count_agents = len(agents_all_list)
    print('Количество агентов:', count_agents)

    if count_agents > 0:
        for agent in agents_all_list:
            print("Agent", agent["number_id"], ":", agent["agent_reg_id"])
            if agent["agent_reg_id"] in agent_reg_id_new:
                try:
                    vvk_scheme_new = formation_agent_update_join(agent, join_scheme_new["scheme"], vvk_scheme_new)
                    db_gui.gui_update_agent_reg_id_reg(agent["number_id"], agent["agent_reg_id"], agent["scheme_revision"], True, None)

                except Exception as e:
                    db_gui.gui_update_agent_reg_id_reg(agent["number_id"], agent["agent_reg_id"], agent["scheme_revision"], False, str(e))
                    db_reg.reg_sch_update_agent_re_reg(agent["number_id"], agent["scheme_revision"], user_query_interval_revision,
                                                       None, None, None)
                    print(e)
            else:
                # необходимо удалить агент с gui, reg_ver
                db_reg.reg_sch_delete_agent(agent["number_id"])
                print("нет такого агента", agent["agent_reg_id"])


    # REG
    db_reg.reg_sch_update_vvk_scheme_all(scheme_revision_vvk_new, join_scheme_new["scheme"], vvk_scheme_new)


    # случай когда ввк схема зарегистрированна!
    vvk_id, _, _, _ = db_sch.sch_ver_select_vvk_details()
    if vvk_id:
        temp = {
            "vvk_id": vvk_id,
            "scheme_revision": scheme_revision_vvk + 1,
            "user_query_interval_revision": user_query_interval_revision
        }
        db_sch.sch_ver_insert_vvk(False, temp, vvk_scheme_new, metric_info_list)


    with open('New.json', 'w') as json_file:
        json.dump(vvk_scheme_new, json_file, indent=4, ensure_ascii=False)



    disconnect(conn)
except:
    sys.exit(1)
    disconnect(conn)