import requests
import copy

from database.database import Database
from myException import MyException427, MyException527

from logger.logger import logger

# !!!
def add_metrics(json_vvk_return_metrics, json_agent_scheme_metrics):
    """
    Добавляет метрики из схемы агента в список метрик схемы VVK, если они отсутствуют.

    Args:
        json_vvk_return_metrics (list): Список метрик схемы VVK.
        json_agent_scheme_metrics (list): Список метрик схемы агента.

    Returns:
        list: Обновленный список метрик схемы VVK.

    Raises:
        ValueError: Если метрика с таким идентификатором уже существует, но имеет различные параметры.
    """
    metrics_list = json_vvk_return_metrics[:]
    for item in json_agent_scheme_metrics:
        existing_metric = next(
            (metric for metric in json_vvk_return_metrics if metric["metric_id"] == item["metric_id"]),
            None)
        if existing_metric:
            if existing_metric != item:
                raise MyException427(
                    f"Metric_id: {item['metric_id']} already exists, but has different parameters.")
        else:
            metrics_list.append(item)
    return metrics_list

# !!!
def add_templates(json_vvk_return_templates, json_agent_scheme_templates):
    """
        Добавляет шаблоны из схемы агента в список шаблонов схемы VVK, если они отсутствуют.

    Args:
        json_vvk_return_templates (list): Список шаблонов схемы VVK.
        json_agent_scheme_templates (list): Список шаблонов схемы агента.

    Returns:
        list: Обновленный список шаблонов схемы VVK.

    Raises:
        ValueError: Если шаблон с таким идентификатором уже существует, но имеет различные параметры.
    """
    templates_list = json_vvk_return_templates[:]
    for item in json_agent_scheme_templates:
        existing_template = next((template for template in json_vvk_return_templates if
                                  template["template_id"] == item["template_id"]), None)
        if existing_template:
            if existing_template != item:
                raise MyException427(
                    f"Template_id: {item['template_id']} already exists, but has different parameters.")
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

# !!!
def if_metric_info(metric_info: dict) -> list:
    """
    Возвращает 'metric_info_list' из словаря metric_info, если оно существует.

    Args:
        metric_info (dict): Словарь, содержащий ключ 'metric_info_list', значение которого будет проверено.

    Returns:
        list: Список, содержащий значение по ключу 'metric_info_list', или пустой список, если значение отсутствует или некорректно.
    """
    if metric_info is None:
        return []

    metric_info_list = metric_info.get('metric_info_list')

    if not metric_info_list or metric_info_list == [None]:
        return []

    return metric_info_list

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

# !!!
def check_full_path_exists(item_list, target_path):
    """
        Проверяет, существует ли указанный путь в списке item_list.
    """
    return not any(item['full_path'] == target_path for item in item_list)

# ??? надо добавить метрик инфо!
def formation_agent_reg_scheme(agent_reg_id: str, agent_scheme: dict, join_scheme: dict, vvk_scheme: dict):
    """
        Формирует схему регистрации агента.

    Args:
        agent_reg_id (str): Регистрационный идентификатор агента.
        agent_scheme (dict): Схема агента.
        join_scheme (dict): Схема Join.
        vvk_scheme (dict): Схема VVK.

    Returns:
        tuple: Кортеж, содержащий схему агента, список агентов в JSON формате и схему VVK.
    """
    json_agent_list = []
    for join_list in join_scheme["join_list"]:
        if agent_reg_id == join_list["agent_reg_id"]:
            # если тип подключения jtInclude
            if join_list["join_type"] == "jtInclude":

                # проверка и добавление metrics
                vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent_scheme['scheme']['metrics'])
                # проверка и добавление templates
                vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent_scheme['scheme']['templates'])

                if agent_scheme["scheme"]["join_id_list"] is not None:
                    for item in agent_scheme["scheme"]["join_id_list"]:
                        full_path_item = join_list["join_item_full_path"] + '/' + item["full_path"]
                        if check_full_path_exists(join_scheme["item_id_list"], full_path_item):
                            raise MyException427(
                                f"Error registering agent for connection type 'jtInclude': path was not found in Jion: {full_path_item}")


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
                    raise MyException427("Error registering agent for connection type 'jtAssign': different number of join_id_list.")

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
                        raise MyException427(f"No join_id:{join_id_list_scheme['agent_item_join_id']} in join_id_list")
    return agent_scheme, json_agent_list, vvk_scheme


# ___________ работа только с БД _________

# !!!
def registration_agent_reg_id_scheme(agent_reg_id: str, all_agent_scheme: dict, db: Database):
    """
        Регистрирует агента.

    Args:
        agent_reg_id (str): Регистрационный идентификатор агента.
        all_agent_scheme (dict): JSON агента.
        db: Ссылка на объект базы данных.

    Returns:
        dict: Возвращает список зарегистрированных "item_id"

    Raises:
        BlockingIOError: Если блокировка базы данных активна.
    """
    # REG_SCH
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, metric_info_list_raw = db.reg_sch_select_vvk_all()
    metric_info_list = if_metric_info(metric_info_list_raw) # ???

    agent_scheme, json_agent_list, vvk_scheme_new = formation_agent_reg_scheme(agent_reg_id, all_agent_scheme, join_scheme, vvk_scheme)

    db.gui_update_vvk_reg_none(scheme_revision_vvk + 1, user_query_interval_revision)
    # может и не надо +1 - может быть ошибка при регистрации агента, когда схема ВВК зарегистрирована
    db.reg_sch_update_vvk_scheme(scheme_revision_vvk + 1, vvk_scheme_new)

    index = db.reg_sch_select_count_agents() + 1
    json_agent_return = {
        "agent_id": index,
        "item_id_list": json_agent_list
    }

    db.gui_update_agent_reg_id_reg_true(index, agent_reg_id, all_agent_scheme["scheme_revision"])
    db.reg_sch_insert_agent(index, agent_reg_id, all_agent_scheme["scheme_revision"], user_query_interval_revision, all_agent_scheme["scheme"], agent_scheme["scheme"])

    # SCH - случай когда ввк схема зарегистрированна!
    vvk_id = db.sch_ver_select_check_vvk_id()
    metric_info_list_dict = {
        "metric_info_list": metric_info_list
    }
    if vvk_id:
        if db.sch_ver_select_latest_status():
            db.sch_ver_insert_vvk(False, vvk_id, scheme_revision_vvk + 1, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_dict)
        else:
            db.sch_ver_update_vvk_if_false(scheme_revision_vvk + 1, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_dict)
            print("RERERERERERER")

    db.reg_sch_block_false()
    return json_agent_return

# !!!
def re_registration_agent_id_scheme(agent_id: int, agent_reg_id: str, all_agent_scheme: dict, db):
    """
        Перерегистрирует агента.

    Args:
        agent_id (str): Идентификатор агента.
        agent_reg_id (str): Регистрационный идентификатор агента.
        all_agent_scheme (dict): JSON агента.
        db: Ссылка на объект базы данных.

    Returns:
        dict: Возвращает список "item_id"

    Raises:
        BlockingIOError: Если блокировка базы данных активна.
    """
    # REG_SCH
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, metric_info_list_raw = db.reg_sch_select_vvk_all()
    metric_info_list = if_metric_info(metric_info_list_raw) # ???


    # получение данных с помощью которых будет произоводиться очистка
    metrics_list_excluding_agent = db.reg_sch_select_metrics_excluding_agent(agent_id)
    templates_list_excluding_agent = db.reg_sch_select_templates_excluding_agent(agent_id)
    full_paths_agent = db.reg_sch_select_full_paths_agent(agent_id) # в теории можно достать еще и item_id

    templates_new = delete_templates(vvk_scheme["templates"], templates_list_excluding_agent)
    metrics_new = delete_metrics(vvk_scheme["metrics"], metrics_list_excluding_agent)
    item_id_list_new = delete_item_id_list(vvk_scheme["item_id_list"], full_paths_agent)
    item_info_list_new = delete_item_info_list(vvk_scheme['item_info_list'], join_scheme['item_info_list'], full_paths_agent)
    # Тут надо написать алгоритм, который будет удалять лишние Метрикинфо по итем айди и метрик айди ???

    vvk_scheme_after_cleaning = {
        "metrics": metrics_new,
        "templates": templates_new,
        "item_id_list": item_id_list_new,
        "item_info_list": item_info_list_new,
    }

    # а потом зарегистрировать заново агент, используя старый метод!

    agent_scheme, json_agent_list, vvk_scheme_new = formation_agent_reg_scheme(agent_reg_id, all_agent_scheme,
                                                                               join_scheme, vvk_scheme_after_cleaning)

    db.gui_update_vvk_reg_none(scheme_revision_vvk + 1, user_query_interval_revision)
    db.reg_sch_update_vvk_scheme(scheme_revision_vvk + 1, vvk_scheme_new)

    json_agent_return = {
        "agent_id": agent_id,
        "item_id_list": json_agent_list
    }

    db.gui_update_agent_id_reg_true(agent_id, all_agent_scheme["scheme_revision"])
    db.reg_sch_update_agent_re_reg(agent_id, all_agent_scheme["scheme_revision"], user_query_interval_revision,
                                   all_agent_scheme["scheme"], agent_scheme["scheme"])

    # SCH - случай когда ввк схема зарегистрированна!
    vvk_id = db.sch_ver_select_check_vvk_id()
    metric_info_list_dict = {
        "metric_info_list": metric_info_list
    }
    if vvk_id:
        if db.sch_ver_select_latest_status():
            db.sch_ver_insert_vvk(False, vvk_id, scheme_revision_vvk + 1, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_dict)
        else:
            db.sch_ver_update_vvk_if_false(scheme_revision_vvk + 1, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_dict)
            print("RERERERERERER")

    db.reg_sch_block_false()
    return json_agent_return

