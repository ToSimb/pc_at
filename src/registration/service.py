import requests
import copy

from logger.logger import logger
from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT

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

def request_registration_vvk(url: str, json_vvk_return: dict):
    headers = {'Content-Type': 'application/json'}
    try:
        logger.info(f"Отправка: {url}")
        response = requests.post(url, json=json_vvk_return, headers=headers)
        if response.status_code == 200:
            logger.info("Успушная регистрация VvkScheme на стороне АФ")
            return response.json()
        else:
            error_str = "(ValueError)Произошла ошибка при регистрации: " + str(response.status_code) + " : " + str(response.text)
            raise ValueError(error_str)
    except requests.RequestException as e:
        logger.error(f"(RequestException)Произошла ошибка при регистрации: {e}")
        raise ValueError(e)

def formation_agent_reg_scheme(agent_reg_id: str, agent_scheme: dict, join_scheme: dict, vvk_scheme: dict):
    json_agent_list = []
    for join_list in join_scheme["join_list"]:
        if agent_reg_id == join_list["agent_reg_id"]:
            # если тип подключения jtInclude
            if join_list["join_type"] == "jtInclude":
                try:
                    # проверка и добавление metrics
                    vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent_scheme['scheme']['metrics'])
                    # проверка и добавление templates
                    vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent_scheme['scheme']['templates'])
                except ValueError as e:
                    raise ValueError(e)

                # поиск самого большого item_id
                if vvk_scheme["item_id_list"]:
                    index = max(
                        item['item_id'] for item in vvk_scheme["item_id_list"] if 'item_id' in item)
                else:
                    index = 0
                # Формирование нового item_id_list
                for a in agent_scheme["scheme"]["item_id_list"]:
                    b = copy.deepcopy(a)
                    index += 1
                    a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
                    a["item_id"] = index
                    b["item_id"] = index
                    for existing_item in vvk_scheme["item_id_list"]:
                        if existing_item["full_path"] == a["full_path"]:
                            existing_item["item_id"] = a["item_id"]
                            break
                    else:
                        vvk_scheme["item_id_list"].append(a)
                    json_agent_list.append(b)
                # Формирование нового item_info_list
                for a in agent_scheme["scheme"]["item_info_list"]:
                    a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
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

                        # поиск самого большого item_id
                        if vvk_scheme["item_id_list"]:
                            index = max(
                                item['item_id'] for item in vvk_scheme["item_id_list"] if
                                'item_id' in item)
                        else:
                            index = 0

                        # формирование списка item_id_list
                        for a in agent_scheme["scheme"]["item_id_list"]:
                            if a["full_path"].split('/')[0] == join_id_list_agent["full_path"]:
                                b = copy.deepcopy(a)
                                a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                    "full_path"].replace(
                                    a["full_path"].split('/')[0], "")
                                index += 1
                                a["item_id"] = index
                                b["item_id"] = index
                                for existing_item in vvk_scheme["item_id_list"]:
                                    if existing_item["full_path"] == a["full_path"]:
                                        existing_item["item_id"] = a["item_id"]
                                        break
                                else:
                                    vvk_scheme["item_id_list"].append(a)
                                json_agent_list.append(b)

                        # формирование списка item_info_list
                        for a in agent_scheme["scheme"]["item_info_list"]:
                            if a["full_path"] == join_id_list_agent["full_path"]:
                                a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                    "full_path"].replace(
                                    a["full_path"].split('/')[0], "")
                                b = next(
                                    (b for b in vvk_scheme["item_info_list"] if
                                     b["full_path"] == a["full_path"]),
                                    None)
                                if b:
                                    b.update(a)
                                else:
                                    vvk_scheme["item_info_list"].append(a)

                    else:
                        raise ValueError("Ошибка: нет join_id:{} в join_id_list".format(
                            join_id_list_scheme["agent_item_join_id"]))
    return agent_scheme, json_agent_list, vvk_scheme

# ___________ работа только с БД _________

def registration_join_scheme(join_scheme: dict, db) -> bool:
    # REG_SCH
    if db.reg_sch_block_check():
        raise BlockingIOError

    if db.reg_sch_select_check_vvk():
# __ ПЕРЕРИГИСТРАЦИЯ __
        return False
    else:
# __ РЕГИСТРАЦИЯ __
        # Формируем структуру VvkScheme:Scheme
        vvk_scheme = {
            "metrics": [],
            "templates": join_scheme["scheme"]["templates"],
            "item_id_list": [],
            "item_info_list": join_scheme["scheme"]["item_info_list"]
        }
        item_id_list = []
        index = 0
        for a in join_scheme["scheme"]["item_id_list"]:
            item_id_list.append({"full_path": a["full_path"], "item_id": index})
            index += 1
        vvk_scheme["item_id_list"] = item_id_list

        # GUI
        vvk_puth = join_scheme["scheme"]["item_id_list"][0]["full_path"].split("/")[0]
        vvk_name = [item for item in join_scheme["scheme"]["templates"] if item.get('template_id') == vvk_puth][0][
            "name"]
        agent_reg_id = [item["agent_reg_id"] for item in join_scheme["scheme"]["join_list"]]

        db.gui_insert_join_scheme(vvk_name, agent_reg_id)

        # REG_SCH
        db.reg_sch_insert_vvk(join_scheme["scheme_revision"], join_scheme["scheme"], vvk_scheme, None)
        return True

def registration_agent_reg_id_scheme(agent_reg_id: str, all_agent_scheme: dict, db):
    # REG_SCH
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, metric_info_list = db.reg_sch_select_vvk_all()

    agent_scheme, json_agent_list, vvk_scheme_new = formation_agent_reg_scheme(agent_reg_id, all_agent_scheme, join_scheme, vvk_scheme)

    db.reg_sch_update_vvk_scheme(scheme_revision_vvk, vvk_scheme_new)

    index = db.reg_sch_select_count_agents() + 1
    json_agent_return = {
        "agent_id": index,
        "item_id_list": json_agent_list
    }
    db.gui_update_agent_reg_id_reg(index, agent_reg_id, all_agent_scheme["scheme_revision"], True)
    db.reg_sch_insert_agent(index, agent_reg_id, all_agent_scheme["scheme_revision"], user_query_interval_revision, all_agent_scheme["scheme"], agent_scheme["scheme"], None)

    db.reg_sch_block_false()
    return json_agent_return


def re_registration_agent_id_scheme(agent_id: int, agent_reg_id: str, all_agent_scheme: dict,
                                    original_scheme_old_agent: dict, scheme_old_agent: dict, metric_info_list_old_agent: dict, db):
    # REG_SCH
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    json_agent_return = []
    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, metric_info_list = db.reg_sch_select_vvk_all()

    # получение данных с помощью которых будет произоводиться очистка
    metrics_list_excluding_agent = db.reg_sch_select_metrics_excluding_agent(agent_id)
    templates_list_excluding_agent = db.reg_sch_select_templates_excluding_agent(agent_id)
    full_paths_agent = db.reg_sch_select_full_paths_agent(agent_id)

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

    # а потом зарегистрировать заново агент, испольщую старый метод!

    agent_scheme, json_agent_list, vvk_scheme_new = formation_agent_reg_scheme(agent_reg_id, all_agent_scheme, join_scheme, vvk_scheme_after_cleaning)

    db.reg_sch_update_vvk_scheme(scheme_revision_vvk + 1, vvk_scheme_new)

    json_agent_return = {
        "agent_id": agent_id,
        "item_id_list": json_agent_list
    }

    db.gui_update_agent_id_reg(agent_id, all_agent_scheme["scheme_revision"], True)

    db.reg_sch_update_agent_re_reg(agent_id, all_agent_scheme["scheme_revision"], user_query_interval_revision, all_agent_scheme["scheme"], agent_scheme["scheme"], None)

    # случай когда ввк схема зарегистрированна!
    vvk_id, _, _, _ = db.sch_ver_select_vvk_details()
    if vvk_id:
        temp = {
            "vvk_id": vvk_id,
            "scheme_revision": scheme_revision_vvk + 1,
            "user_query_interval_revision": user_query_interval_revision
        }
        db.sch_ver_insert_vvk(False, temp, vvk_scheme_new, metric_info_list)

    db.reg_sch_block_false()
    return json_agent_return

def registration_vvk_scheme(db):
    # REG_SCH
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    vvk_id, _, _, _ = db.sch_ver_select_vvk_details()
    if vvk_id:
        return ("Данный метрод можно использовать только для первичной регистрации")

    scheme_revision, scheme, metric_info_list = db.reg_sch_select_vvk_scheme()
    data = {
        "scheme_revision": scheme_revision,
        "scheme": scheme
    }
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/vvk-scheme'
    url = f'http://127.0.0.1:8000/agent-scheme/save'
    temp = request_registration_vvk(url, data)

    # GUI
    db.gui_update_vvk_reg(temp["vvk_id"], temp["scheme_revision"], temp["user_query_interval_revision"], True)
    # SCH_VER
    db.sch_ver_insert_vvk(True, temp, scheme, metric_info_list)

    # REG_SCH
    db.reg_sch_update_vvk_id(temp["vvk_id"])
    db.reg_sch_update_all_user_query_revision(temp["user_query_interval_revision"])

    db.reg_sch_block_false()
    return temp

