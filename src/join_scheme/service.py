import copy
import json
import time

from myException import MyException427

from database.database import Database

from logger.logger import logger

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
    metrics_list = copy.deepcopy(json_vvk_return_metrics)
    for item in json_agent_scheme_metrics:
        existing_metric = next(
            (metric for metric in metrics_list if metric["metric_id"] == item["metric_id"]),
            None)
        if existing_metric:
            if existing_metric["type"] != item["type"]:
                raise MyException427("(RU) Метрика '{item['metric_id']}' имеет расхождение в 'type'! (ENG) The metric '{item['metric_id']}' has a discrepancy in 'type'")
            if existing_metric["dimension"] != item["dimension"]:
                raise MyException427("RU) Метрика '{item['metric_id']}' имеет расхождение в 'dimension'! (ENG) The metric '{item['metric_id']}' has a discrepancy in 'dimension'")
            if existing_metric["query_interval"] != item["query_interval"]:
                raise MyException427("RU) Метрика '{item['metric_id']}' имеет расхождение в 'query_interval'! (ENG) The metric '{item['metric_id']}' has a discrepancy in 'query_interval'")
            # if existing_metric != item:
                # raise MyException427(
                    # f"(RU) Метрика '{item['metric_id']}' имеет расхождение в параметрах! (ENG) The metric '{item['metric_id']}' has a discrepancy in parameters")
        else:
            metrics_list.append(item)
    return metrics_list

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
    # templates_list = json_vvk_return_templates[:]
    templates_list = copy.deepcopy(json_vvk_return_templates)
    for item in json_agent_scheme_templates:
        existing_template = next((template for template in templates_list if
                                  template["template_id"] == item["template_id"]), None)
        if existing_template:
            if existing_template.get("includes"):
                print(existing_template)
                if existing_template.get("includes") != item.get("includes"):
                    raise MyException427("(RU) Шаблон '{item['template_id']}' имеет расхождение в 'includes'! (ENG) The template '{item['template_id']}' has a discrepancy in 'includes'.")
            if existing_template.get("metrics"):
                if existing_template.get("metrics").sort() != item.get("metrics").sort():
                    raise MyException427("(RU) Шаблон '{item['template_id']}' имеет расхождение в 'metrics'! (ENG) The template '{item['template_id']}' has a discrepancy in 'metrics'.")
            # if existing_template != item:
                # raise MyException427(
                #     f"(RU) Шаблон '{item['template_id']}' имеет расхождение в параметрах! (ENG) The template '{item['template_id']}' has a discrepancy in parameters.")
        else:
            templates_list.append(item)
    return templates_list

def check_correctness_of_templates(agent_path, join_path):
    a = agent_path.split("[")[0]
    b = join_path.split("/")[-1].split("[")[0]
    if a != b:
        raise ValueError(f"(RU) Ошибка входящих шаблонов, шаблон '{agent_path}' не найден. "
                         f"(ENG) Incoming templates error, template '{agent_path}' not found.")

def check_full_path_exists(item_list, target_path):
    """
        Проверяет, существует ли указанный путь в списке 'item_id_list' join схемы.

    Args:
        item_list (list): Список 'item_id_list', в котором выполняется поиск.
        target_path (str): Целевой путь для поиска.

    Returns:
        bool: Возвращает True, если путь не найден, и False, если путь найден.

    """
    for item in item_list:
        if item['full_path'] == target_path:
            return False
    return True

def formation_agent_update_join(agent: dict, join_scheme: dict, vvk_scheme: dict):
    """
        Обновляет схему VVK на основе схемы агента и join схемы.

    Args:
        agent (dict): Агент, содержащий все информацию из БД.
        join_scheme (dict): Join схема, содержащая списки подключений и их типы.
        vvk_scheme (dict): Схема VVK, которую необходимо обновить.

    Returns:
        dict: Обновленная схема VVK.

    Raises:
        ValueError: Если возникают ошибки при добавлении метрик, шаблонов или проверке путей.
    """
    for join_list in join_scheme["join_list"]:
        if agent["agent_reg_id"] == join_list["agent_reg_id"]:
            # если тип подключения jtInclude
            if join_list["join_type"] == "jtInclude":
                try:
                    # проверка и добавление metrics
                    vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent['scheme']['metrics'])
                    # проверка и добавление templates
                    vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent['scheme']['templates'])
                except ValueError as e:
                    raise ValueError(e)

                for item in agent["scheme"]["join_id_list"]:
                    full_path_item = join_list["join_item_full_path"] + '/' + item["full_path"]
                    if check_full_path_exists(join_scheme["item_id_list"], full_path_item):
                        raise ValueError(
                            f"(RU) Ошибка регистрации 'jtInclude': нет пути '{full_path_item}' в Join. "
                            f"(ENG) Error registering 'jtInclude': No path '{full_path_item}' in Join.")

                # Формирование нового item_id_list
                for a in agent["response_scheme"]["item_id_list"]:
                    a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
                    for existing_item in vvk_scheme["item_id_list"]:
                        if existing_item["full_path"] == a["full_path"]:
                            existing_item["item_id"] = a["item_id"]
                            break
                    else:
                        vvk_scheme["item_id_list"].append(a)

                # Формирование нового item_info_list
                for a in agent["original_scheme"]["item_info_list"]:
                    a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
                    b = next(
                        (b for b in vvk_scheme["item_info_list"] if
                         b["full_path"] == a["full_path"]),
                        None)
                    if b:
                        b.update(a)
                    else:
                        vvk_scheme["item_info_list"].append(a)

            # если тип подключения jtAssign
            if join_list["join_type"] == "jtAssign":
                # проверка и добавление metrics
                vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent['scheme']['metrics'])
                # проверка и добавление templates
                vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent['scheme']['templates'])

                if len(join_list["joins"]) != len(agent["scheme"]["join_id_list"]):
                    raise ValueError("(RU) Ошибка регистрации 'jtAssign': Не совпадает количество точек подключения в join_id_list. "
                                     "(ENG) Error registering 'jtAssign': The number of connection points does not match.")

                # проходимся по join_id_list в json_agent_scheme
                for join_id_list_scheme in join_list["joins"]:
                    item_join_id_list_agent = next(
                        (join_id_list_agent for join_id_list_agent in agent["scheme"]["join_id_list"]
                         if join_id_list_scheme["agent_item_join_id"] == join_id_list_agent["join_id"]), None)
                    if item_join_id_list_agent:
                        # формирование списка item_id_list
                        for a in agent["response_scheme"]["item_id_list"]:
                            if a["full_path"].split('/')[0] == item_join_id_list_agent["full_path"]:
                                check_correctness_of_templates(a["full_path"],
                                                           join_id_list_scheme["join_item_full_path"])
                                a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                    "full_path"].replace(
                                    a["full_path"].split('/')[0], "", 1)
                                for existing_item in vvk_scheme["item_id_list"]:
                                    if existing_item["full_path"] == a["full_path"]:
                                        existing_item["item_id"] = a["item_id"]
                                        break
                                else:
                                    vvk_scheme["item_id_list"].append(a)

                        # формирование списка item_info_list
                        for a in agent["original_scheme"]["item_info_list"]:
                            if a["full_path"].split('/')[0] == item_join_id_list_agent["full_path"]:
                                a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                    "full_path"].replace(
                                    a["full_path"].split('/')[0], "", 1)
                                b = next(
                                    (b for b in vvk_scheme["item_info_list"] if
                                     b["full_path"] == a["full_path"]),
                                    None)
                                if b:
                                    b.update(a)
                                else:
                                    vvk_scheme["item_info_list"].append(a)

                    else:
                        raise ValueError(f"(RU) Нет join_id '{join_id_list_scheme['agent_item_join_id']}' в join_id_list Агента. "
                                         f"(ENG) No join_id '{join_id_list_scheme['agent_item_join_id']}' in join_id_list in Agent")

    return vvk_scheme

def checking_correctness_patch_from_join_list(join_scheme):
    for item_join_list in join_scheme["scheme"]["join_list"]:
        if item_join_list["join_type"] == "jtInclude":
            if check_full_path_exists(join_scheme["scheme"]["item_id_list"], item_join_list["join_item_full_path"]):
                raise MyException427(f"(RU) Не правильно описан путь для агента '{item_join_list['agent_reg_id']}'. "
                                     f"(ENG) The path for agent '{item_join_list['agent_reg_id']}' is not described correctly.")
        elif item_join_list["join_type"] == "jtAssign":
            for item_joins in item_join_list["joins"]:
                if check_full_path_exists(join_scheme["scheme"]["item_id_list"], item_joins["join_item_full_path"]):
                    raise MyException427(f"(RU) Не правильно описан путь для агента '{item_join_list['agent_reg_id']}'. "
                                         f"(ENG) The path for agent '{item_join_list['agent_reg_id']}' is not described correctly.")
        else:
            raise MyException427(f"(RU) Не правильно указан тип подключения '{item_join_list['join_type']}'. "
                                 f"(ENG) The connection type is specified incorrectly '{item_join_list['join_type']}'.")

# ___________ работа только с БД _________

def delete_metric_info_agent(agent_id: int, metric_info: dict, db: Database):
    """
        Удаляет из `metric_info` элементы принадлежащие агенту agent_id.

    Args:
        agent_id (int): Идентификатор агента.
        metric_info (dict): Словарь, содержащий информацию о метриках.
        db (Database): Объект базы данных.

    Returns:
        dict: Словарь с ключом 'metric_info_list', значение которого является отфильтрованным списком метрик.
    """
    metric_info_list = if_metric_info(metric_info)
    if metric_info_list == []:
        return metric_info
    else:
        _, _, metrics_id, items_id = db.reg_sch_select_metrics_and_items_for_agent(agent_id)
        metric_info_list_new = []
        for item in metric_info_list:
            if not (str(item["item_id"]) in items_id and item["metric_id"] in metrics_id):
                metric_info_list_new.append(item)
        metric_info_list_dict = {
            "metric_info_list": metric_info_list_new
        }
        return metric_info_list_dict

def registration_join_scheme(join_scheme: dict, db: Database) -> dict:
    """
        Первичная регистрирует схему ВВК в базе данных и возвращает ее структуру в словаре.

    Args:
        join_scheme (dict): Словарь с информацией о схеме объединения,
        db: Объект, предоставляющий доступ к базе данных.

    Returns:
        dict: Структура данных VvkScheme, содержащая информацию о зарегистрированной схеме объединения.

    Raises:
        BlockingIOError: Если функция reg_sch_block_check() возвращает True, это означает, что регистрация заблокирована.
    """
    # REG_SCH
    if db.reg_sch_block_check():
        raise BlockingIOError
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

    # проверка путей!
    checking_correctness_patch_from_join_list(join_scheme)

    # GUI
    vvk_puth = join_scheme["scheme"]["item_id_list"][0]["full_path"].split("/")[0]
    vvk_name = [item for item in join_scheme["scheme"]["templates"] if item.get('template_id') == vvk_puth][0]["name"]
    agents_reg_id = [item["agent_reg_id"] for item in join_scheme["scheme"]["join_list"]]

    db.gui_insert_join_scheme(vvk_name, agents_reg_id)
    # REG_SCH
    metric_info_list_dict = {
        "metric_info_list": []
    }

    db.reg_sch_insert_vvk(join_scheme["scheme_revision"], join_scheme["scheme"], vvk_scheme, index, metric_info_list_dict)
    return vvk_scheme

def re_registration_join_scheme(join_scheme_new, user_query_interval_revision, metric_info_list_raw,
                                vvk_scheme_old: dict, max_index: int, db: Database) -> dict:
    """
        Перерегистрация схемы VVK.

    Args:
        join_scheme_new (dict): Новая join схема.
        user_query_interval_revision (int): Ревизия интервала пользовательских запросов.
        metric_info_list (list): Список информации о метриках.
        db: Объект для работы с базой данных.

    Returns:
        dict: Возвращает новую схему соединения VvkSchemeNew.
    """
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    # Формируем структуру VvkSchemeNew:Scheme
    vvk_scheme_new = {
        "metrics": [],
        "templates": join_scheme_new["scheme"]["templates"],
        "item_id_list": [],
        "item_info_list": join_scheme_new["scheme"]["item_info_list"]
    }

    index = max_index
    item_id_list = []
    item_id_list_vvk = vvk_scheme_old['item_id_list']

    # Формирование нового item_id_list по новой JoinScheme
    join_scheme_new_copy = copy.deepcopy(join_scheme_new)
    for a in join_scheme_new_copy["scheme"]["item_id_list"]:
        # изменения - вернуть старые item_id !!
        for item in item_id_list_vvk:
            if item['full_path'] == a["full_path"]:
                a["item_id"] = item["item_id"]
                break
        else:
            a["item_id"] = index
            index += 1
        item_id_list.append({"full_path": a["full_path"], "item_id": a["item_id"]})

    vvk_scheme_new["item_id_list"] = item_id_list

    # проверка путей!
    checking_correctness_patch_from_join_list(join_scheme_new)

    # GUI
    vvk_puth = join_scheme_new["scheme"]["item_id_list"][0]["full_path"].split("/")[0]
    vvk_name = [item for item in join_scheme_new["scheme"]["templates"] if item.get('template_id') == vvk_puth][0]["name"]
    db.gui_update_vvk_name(vvk_name)

    db.gui_delete_agents()
    agent_reg_id_new = [item["agent_reg_id"] for item in join_scheme_new["scheme"]["join_list"]]
    db.gui_insert_agents(agent_reg_id_new)

    # получаем схемы агентов
    agents_all_list = db.reg_sch_select_agents_all_json()
    count_agents = len(agents_all_list)

    # если старый агент есть в новой схеме, то он восстанавливается в новой схеме ВВВ
    if count_agents > 0:
        for agent in agents_all_list:
            if agent["agent_reg_id"] in agent_reg_id_new:
                try:
                    vvk_scheme_new_copy = copy.deepcopy(vvk_scheme_new)
                    vvk_scheme_new = formation_agent_update_join(agent, join_scheme_new_copy["scheme"], vvk_scheme_new_copy)
                    db.gui_update_agent_reg_id_reg_true(agent["number_id"], agent["agent_reg_id"],
                                                        agent["scheme_revision"])
                except Exception as e:
                    metric_info_list_raw = delete_metric_info_agent(agent["number_id"], metric_info_list_raw, db)
                    db.gui_update_agent_reg_id_update_error(agent["number_id"], agent["agent_reg_id"],
                                                            agent["scheme_revision"], str(e))
            else:
                metric_info_list_raw = delete_metric_info_agent(agent["number_id"], metric_info_list_raw, db)
                db.reg_sch_delete_agent(agent["number_id"])

    # GUI
    db.gui_update_vvk_reg_none(join_scheme_new["scheme_revision"], user_query_interval_revision)

    # REG
    db.reg_sch_update_vvk_scheme_all(join_scheme_new["scheme_revision"], join_scheme_new["scheme"], vvk_scheme_new, index, metric_info_list_raw)

    # SCH - случай когда ввк схема зарегистрирована!
    vvk_id = db.sch_ver_select_check_vvk_id()
    if vvk_id:
        if db.sch_ver_select_latest_status():
            db.sch_ver_insert_vvk(False, vvk_id, join_scheme_new["scheme_revision"], user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_raw)
        else:
            db.sch_ver_update_vvk_if_false(join_scheme_new["scheme_revision"], user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_raw)

    db.reg_sch_block_false()
    return vvk_scheme_new
