import requests
import copy
import json

from database.database import Database
from myException import MyException427, MyException527, MyException528

from logger.logger import logger


def save_to_json(agent_id, suffix, data):
    filename = f"files/{suffix}/agent_{agent_id}.json"
    logger.info(f"Агент {agent_id} сохранен в файл {filename}")
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def save_item_ids(index_agent, json_agent_return, json_agent_scheme):
    save_to_json(index_agent, "list", json_agent_return)

    # потом лучше удалить
    save_to_json(index_agent, "scheme", json_agent_scheme)

    item_ids_list = []
    item_ids_sch = []
    for item in json_agent_return["item_id_list"]:
        item_ids_list.append(item["item_id"])
    for item in json_agent_scheme:
        item_ids_sch.append(item["item_id"])

    logger.debug(f"Агент {index_agent} имеет следующие item_id: {item_ids_list}")
    logger.debug(f"Агент {index_agent} имеет следующие item_id: {item_ids_sch}")

    try:
        if item_ids_list.sort() == item_ids_sch.sort():
            logger.debug("Списки содержат одинаковые элементы")
        else:
            logger.debug("Списки содержат разные элементы")
    except Exception as e:
        str_error = "(RU) Ошибка при выдаче item_id. (ENG) Error when issuing item_id :" + str(e)
        raise MyException528(str_error)

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
                raise MyException427(f"(RU) Метрика '{item['metric_id']}' имеет расхождение в 'type'! (ENG) The metric '{item['metric_id']}' has a discrepancy in 'type'")
            if existing_metric["dimension"] != item["dimension"]:
                raise MyException427(f"RU) Метрика '{item['metric_id']}' имеет расхождение в 'dimension'! (ENG) The metric '{item['metric_id']}' has a discrepancy in 'dimension'")
            if existing_metric["query_interval"] != item["query_interval"]:
                raise MyException427(f"RU) Метрика '{item['metric_id']}' имеет расхождение в 'query_interval'! (ENG) The metric '{item['metric_id']}' has a discrepancy in 'query_interval'")
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
                    raise MyException427(f"(RU) Шаблон '{item['template_id']}' имеет расхождение в 'includes'! (ENG) The template '{item['template_id']}' has a discrepancy in 'includes'.")
            if existing_template.get("metrics"):
                if existing_template.get("metrics").sort() != item.get("metrics").sort():
                    raise MyException427(f"(RU) Шаблон '{item['template_id']}' имеет расхождение в 'metrics'! (ENG) The template '{item['template_id']}' has a discrepancy in 'metrics'.")
            # if existing_template != item:
                # raise MyException427(
                #     f"(RU) Шаблон '{item['template_id']}' имеет расхождение в параметрах! (ENG) The template '{item['template_id']}' has a discrepancy in parameters.")
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

def check_full_path_exists(item_list, target_path):
    """
        Проверяет, существует ли указанный путь в списке item_list.
    """
    return not any(item['full_path'] == target_path for item in item_list)

def check_correctness_of_templates(agent_path, join_path):
    a = agent_path.split("[")[0]
    b = join_path.split("/")[-1].split("[")[0]
    if a != b:
        raise MyException427(f"(RU) Ошибка входящих шаблонов, шаблон '{agent_path}' не найден. (ENG) Incoming templates error, template '{agent_path}' not found.")

def formation_agent_reg_scheme(agent_reg_id: str, agent_scheme: dict, join_scheme: dict, vvk_scheme: dict,
                               max_index: int, item_id_list_agent: list):
    """
        Формирует схему регистрации агента.

    Args:
        agent_reg_id (str): Регистрационный идентификатор агента.
        agent_scheme (dict): Схема агента.
        join_scheme (dict): Схема Join.
        vvk_scheme (dict): Схема VVK.
        max_index (int): Максимальный индекс.
        item_id_list_agent (list): Старые item_id агента.

    Returns:
        tuple: Кортеж, содержащий схему агента, список агентов в JSON формате и схему VVK, а так же item_id(совпадения)
        для перерегистрированного агента + MAX_INDEX.
    """
    json_agent_list = []
    index = max_index
    for join_list in join_scheme["join_list"]:
        if agent_reg_id == join_list["agent_reg_id"]:
            # если тип подключения jtInclude
            if join_list["join_type"] == "jtInclude":

                # проверка и добавление metrics
                vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent_scheme['scheme']['metrics'])
                # проверка и добавление templates
                vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent_scheme['scheme']['templates'])

                all_initial_agent_paths = []
                if agent_scheme["scheme"]["join_id_list"] is not None:
                    for item in agent_scheme["scheme"]["join_id_list"]:
                        all_initial_agent_paths.append(item['full_path'])
                        full_path_item = join_list["join_item_full_path"] + '/' + item["full_path"]
                        if check_full_path_exists(join_scheme["item_id_list"], full_path_item):
                            raise MyException427(
                                f"(RU) Ошибка регистрации 'jtInclude': нет пути '{full_path_item}' в Join. "
                                f"(ENG) Error registering 'jtInclude': No path '{full_path_item}' in Join.")
                # Формирование нового item_id_list
                for a in agent_scheme["scheme"]["item_id_list"]:
                    # проверка на корректность путей в item_id_list
                    if a["full_path"].split('/')[0] in all_initial_agent_paths:
                        b = copy.deepcopy(a)
                        a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
                        # изменения - вернуть старые item_id !!
                        for item in item_id_list_agent:
                            if item['full_path'] == a["full_path"]:
                                a["item_id"] = item["item_id"]
                                b["item_id"] = item["item_id"]
                                break
                        else:
                            a["item_id"] = index
                            b["item_id"] = index
                            index += 1
                        for existing_item in vvk_scheme["item_id_list"]:
                            if existing_item["full_path"] == a["full_path"]:
                                existing_item["item_id"] = a["item_id"]
                                break
                        else:
                            vvk_scheme["item_id_list"].append(a)
                        json_agent_list.append(b)
                    else:
                        raise MyException427(
                            f"(RU) Элемент '{a['full_path']}' отсутствует в agent_scheme[scheme][join_id_list]. "
                            f"(ENG) Element '{a['full_path']}' is not in agent_scheme[scheme][join_id_list].")

                # Формирование нового item_info_list
                for a in agent_scheme["scheme"]["item_info_list"]:
                    # проверка на корректность путей в item_info_list
                    if a["full_path"].split('/')[0] in all_initial_agent_paths:
                        a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
                        for b in vvk_scheme["item_info_list"]:
                            if a["full_path"] == b["full_path"]:
                                b.update(a)
                                break
                        else:
                            vvk_scheme["item_info_list"].append(a)
                    else:
                        raise MyException427(f"(RU) Элемент '{a['full_path']}' неправильный в agent_scheme[scheme][item_info_list]. "
                                             f"(ENG) Element '{a['full_path']}' is invalid in agent_scheme[scheme][item_info_list].")
            # если тип подключения jtAssign
            if join_list["join_type"] == "jtAssign":
                all_initial_agent_paths = []
                # проверка и добавление metrics
                vvk_scheme['metrics'] = add_metrics(vvk_scheme['metrics'], agent_scheme['scheme']['metrics'])
                # проверка и добавление templates
                vvk_scheme['templates'] = add_templates(vvk_scheme['templates'], agent_scheme['scheme']['templates'])

                if len(join_list["joins"]) != len(agent_scheme["scheme"]["join_id_list"]):
                    raise MyException427("(RU) Ошибка регистрации 'jtAssign': Не совпадает количество точек подключения в join_id_list. "
                                         "(ENG) Error registering 'jtAssign': The number of connection points does not match.")

                # формируем all_initial_agent_paths для проверки корректности путей
                for join_id_list_scheme in join_list["joins"]:
                    item_join_id_list_agent = next(
                        (join_id_list_agent for join_id_list_agent in agent_scheme["scheme"]["join_id_list"]
                         if join_id_list_scheme["agent_item_join_id"] == join_id_list_agent["join_id"]), None)
                    if item_join_id_list_agent:
                        all_initial_agent_paths.append(item_join_id_list_agent["full_path"])
                    else:
                        raise MyException427(
                            f"(RU) Нет join_id '{join_id_list_scheme['agent_item_join_id']}' в join_id_list Агента. "
                            f"(ENG) No join_id '{join_id_list_scheme['agent_item_join_id']}' in join_id_list in Agent")

                # проверка на корректность путей в item_info_list
                agent_scheme_copy_item_info_list = copy.deepcopy(agent_scheme["scheme"]["item_info_list"])
                for a in agent_scheme_copy_item_info_list:
                    if a["full_path"].split('/')[0] not in all_initial_agent_paths:
                        raise MyException427(
                            f"(RU) Элемент '{a['full_path']}' неправильный в agent_scheme[scheme][item_info_list]. "
                            f"(ENG) Element '{a['full_path']}' is invalid in agent_scheme[scheme][item_info_list].")

                # проходимся по join_id_list в json_agent_scheme
                for join_id_list_scheme in join_list["joins"]:
                    item_join_id_list_agent = next(
                        (join_id_list_agent for join_id_list_agent in agent_scheme["scheme"]["join_id_list"]
                         if join_id_list_scheme["agent_item_join_id"] == join_id_list_agent["join_id"]), None)
                    if item_join_id_list_agent:
                        for a in agent_scheme["scheme"]["item_id_list"]:
                            if a["full_path"].split('/')[0] == item_join_id_list_agent["full_path"]:

                                # проверка !!!
                                check_correctness_of_templates(a["full_path"],
                                                               join_id_list_scheme["join_item_full_path"])

                                b = copy.deepcopy(a)
                                a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                    "full_path"].replace(
                                    a["full_path"].split('/')[0], "", 1)
                                for item in item_id_list_agent:
                                    if item['full_path'] == a["full_path"]:
                                        a["item_id"] = item["item_id"]
                                        b["item_id"] = item["item_id"]
                                        break
                                else:
                                    a["item_id"] = index
                                    b["item_id"] = index
                                    index += 1
                                for existing_item in vvk_scheme["item_id_list"]:
                                    if existing_item["full_path"] == a["full_path"]:
                                        existing_item["item_id"] = a["item_id"]
                                        break
                                else:
                                    vvk_scheme["item_id_list"].append(a)
                                json_agent_list.append(b)

                        # формирование списка item_info_list
                        for a in agent_scheme["scheme"]["item_info_list"]:
                            if a["full_path"].split('/')[0] == item_join_id_list_agent["full_path"]:
                                a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                    "full_path"].replace(
                                    a["full_path"].split('/')[0], "", 1)
                                for b in vvk_scheme["item_info_list"]:
                                    if a["full_path"] == b["full_path"]:
                                        b.update(a)
                                        break
                                else:
                                    vvk_scheme["item_info_list"].append(a)

                    else:
                        raise MyException427(f"(RU) Нет join_id '{join_id_list_scheme['agent_item_join_id']}' в join_id_list Агента. "
                                             f"(ENG) No join_id '{join_id_list_scheme['agent_item_join_id']}' in join_id_list in Agent")
    return agent_scheme, json_agent_list, vvk_scheme, index

def delete_metric_info(metric_info, item_id_agent, metrics_id_agent):
    """
        Удаляет элементы из `metric_info`, которые соответствуют определенным критериям.

    Args:
        metric_info (dict): Словарь, содержащий информацию о метриках.
        item_id_agent (list): Список идентификаторов элементов.
        metrics_id_agent (list): Список идентификаторов метрик агента.

    Returns:
        dict: Словарь с ключом 'metric_info_list', значение которого является отфильтрованным списком метрик.
    """
    metric_info_list = if_metric_info(metric_info)
    if metric_info_list == []:
        return metric_info
    else:
        metric_info_list_new = []
        for item in metric_info_list:
            if not (item["item_id"] in item_id_agent and item["metric_id"] in metrics_id_agent):
                metric_info_list_new.append(item)
        metric_info_list_dict = {
            "metric_info_list": metric_info_list_new
        }
        return metric_info_list_dict


def add_metric_info_list_dict(metric_info, metric_info_agent):
    """
        Добавляет новые элементы `metric_info`.

    Args:
        metric_info (dict): Словарь, содержащий информацию о метриках.
        metric_info_agent (list): Список метрик инфо агента.

    Returns:
        dict: Словарь с ключом 'metric_info_list', значение которого является отфильтрованным списком метрик.
    """
    metric_info_list = if_metric_info(metric_info)
    if metric_info_list == []:
        metric_info_list_dict = {
            "metric_info_list": metric_info_agent
        }
        return metric_info_list_dict
    else:
        metric_info_list.extend(metric_info_agent)
        metric_info_list_dict = {
            "metric_info_list": metric_info_list
        }
        return metric_info_list_dict

# ___________ работа только с БД _________
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

    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, max_index, metric_info_list_raw = db.reg_sch_select_vvk_all()

    all_agent_scheme_copy = copy.deepcopy(all_agent_scheme)
    agent_scheme, json_agent_list, vvk_scheme_new, max_index = formation_agent_reg_scheme(agent_reg_id, all_agent_scheme_copy,
                                                                               join_scheme, vvk_scheme, max_index, [])

    db.gui_update_vvk_reg_none(scheme_revision_vvk, user_query_interval_revision)
    db.reg_sch_update_vvk_scheme(scheme_revision_vvk, vvk_scheme_new, max_index, metric_info_list_raw)

    index_agent = db.reg_sch_select_max_index_agents() + 1
    json_agent_return = {
        "agent_id": index_agent,
        "item_id_list": json_agent_list
    }

    save_item_ids(index_agent, json_agent_return, agent_scheme["scheme"]["item_id_list"])

    db.gui_update_agent_reg_id_reg_true(index_agent, agent_reg_id, all_agent_scheme["scheme_revision"])
    db.reg_sch_insert_agent(index_agent, agent_reg_id, all_agent_scheme["scheme_revision"], user_query_interval_revision, all_agent_scheme["scheme"], agent_scheme["scheme"], json_agent_return)

    # SCH - случай когда ввк схема зарегистрированна!
    vvk_id = db.sch_ver_select_check_vvk_id()

    if vvk_id:
        if db.sch_ver_select_latest_status():
            db.sch_ver_insert_vvk(False, vvk_id, scheme_revision_vvk, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_raw)
        else:
            db.sch_ver_update_vvk_if_false(scheme_revision_vvk, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_raw)

    db.reg_sch_block_false()
    return json_agent_return

def re_registration_agent_id_scheme(agent_id: int, agent_reg_id: str, all_agent_scheme: dict, db: Database):
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

    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, max_index, metric_info_list_raw = db.reg_sch_select_vvk_all()

    # получение данных с помощью которых будет производиться очистка
    metrics_list_excluding_agent = db.reg_sch_select_metrics_excluding_agent(agent_id)

    templates_list_excluding_agent = db.reg_sch_select_templates_excluding_agent(agent_id)
    templates_list_JoinScheme = db.reg_sch_select_vvk_templates()
    templates_list_excluding_agent.extend(templates_list_JoinScheme)

    item_id_list_agent = db.reg_sch_select_agent_item_id_list(agent_id)
    full_paths_agent = []
    item_id_agent = []
    for item in item_id_list_agent:
        full_paths_agent.append(item["full_path"])
        item_id_agent.append(item["item_id"])
    _, _, metrics_id_agent, _ = db.reg_sch_select_metrics_and_items_for_agent(agent_id)

    # очистка схемы ВВК от агента !
    templates_new = delete_templates(vvk_scheme["templates"], templates_list_excluding_agent)
    metrics_new = delete_metrics(vvk_scheme["metrics"], metrics_list_excluding_agent)
    item_id_list_new = delete_item_id_list(vvk_scheme["item_id_list"], full_paths_agent)
    item_info_list_new = delete_item_info_list(vvk_scheme['item_info_list'], join_scheme['item_info_list'], full_paths_agent)
    metric_info_list_dict = delete_metric_info(metric_info_list_raw, item_id_agent, metrics_id_agent)

    vvk_scheme_after_cleaning = {
        "metrics": metrics_new,
        "templates": templates_new,
        "item_id_list": item_id_list_new,
        "item_info_list": item_info_list_new,
    }

    save_to_json(0, "clear", vvk_scheme_after_cleaning)

    # а потом зарегистрировать заново агент, используя старый метод!
    all_agent_scheme_copy = copy.deepcopy(all_agent_scheme)
    agent_scheme, json_agent_list, vvk_scheme_new, max_index = formation_agent_reg_scheme(agent_reg_id, all_agent_scheme_copy,
                                                                               join_scheme, vvk_scheme_after_cleaning,
                                                                               max_index, item_id_list_agent)


    if all_agent_scheme["metric_info_list"] is not None:
        metric_info_list_dict = add_metric_info_list_dict(metric_info_list_dict, all_agent_scheme["metric_info_list"])



    db.gui_update_vvk_reg_none(scheme_revision_vvk + 1, user_query_interval_revision)
    db.reg_sch_update_vvk_scheme(scheme_revision_vvk + 1, vvk_scheme_new, max_index, metric_info_list_dict)

    json_agent_return = {
        "agent_id": agent_id,
        "item_id_list": json_agent_list
    }

    agent_mil = {
        "metric_info_list": all_agent_scheme["metric_info_list"]
    }

    save_item_ids(agent_id, json_agent_return, agent_scheme["scheme"]["item_id_list"])

    db.gui_update_agent_id_re_reg_true(agent_id, all_agent_scheme["scheme_revision"])
    db.reg_sch_update_agent_re_reg(agent_id, all_agent_scheme["scheme_revision"], user_query_interval_revision,
                                   all_agent_scheme["scheme"], agent_scheme["scheme"], json_agent_return, agent_mil)

    # SCH - случай когда ввк схема зарегистрированна!
    vvk_id = db.sch_ver_select_check_vvk_id()

    if vvk_id:
        if db.sch_ver_select_latest_status():
            db.sch_ver_insert_vvk(False, vvk_id, scheme_revision_vvk + 1, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_dict)
        else:
            db.sch_ver_update_vvk_if_false(scheme_revision_vvk + 1, user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_dict)

    db.reg_sch_block_false()
    return json_agent_return

def delete_agent(agent_id: int, db: Database):
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    scheme_revision_vvk, user_query_interval_revision, join_scheme, vvk_scheme, max_index, metric_info_list_raw = db.reg_sch_select_vvk_all()

    # получение данных с помощью которых будет производиться очистка
    metrics_list_excluding_agent = db.reg_sch_select_metrics_excluding_agent(agent_id)
    agent_reg_id = db.gui_select_agent_reg_id_for_check_agent_reg_id(agent_id)

    templates_list_excluding_agent = db.reg_sch_select_templates_excluding_agent(agent_id)
    templates_list_JoinScheme = db.reg_sch_select_vvk_templates()
    templates_list_excluding_agent.extend(templates_list_JoinScheme)

    item_id_list_agent = db.reg_sch_select_agent_item_id_list(agent_id)
    full_paths_agent = []
    item_id_agent = []
    for item in item_id_list_agent:
        full_paths_agent.append(item["full_path"])
        item_id_agent.append(item["item_id"])
    _, _, metrics_id_agent, _ = db.reg_sch_select_metrics_and_items_for_agent(agent_id)

    # очистка схемы ВВК от агента !
    templates_new = delete_templates(vvk_scheme["templates"], templates_list_excluding_agent)
    metrics_new = delete_metrics(vvk_scheme["metrics"], metrics_list_excluding_agent)
    item_id_list_new = delete_item_id_list(vvk_scheme["item_id_list"], full_paths_agent)
    item_info_list_new = delete_item_info_list(vvk_scheme['item_info_list'], join_scheme['item_info_list'], full_paths_agent)
    metric_info_list_dict = delete_metric_info(metric_info_list_raw, item_id_agent, metrics_id_agent)

    vvk_scheme_after_cleaning = {
        "metrics": metrics_new,
        "templates": templates_new,
        "item_id_list": item_id_list_new,
        "item_info_list": item_info_list_new,
    }

    #GUI
    db.gui_delete_agent_id(agent_id)
    db.gui_insert_agent(agent_reg_id)

    db.reg_sch_block_false()

    #REG_SCH
    db.reg_sch_delete_agent(agent_id)
    db.reg_sch_update_vvk_scheme_from_editor(scheme_revision_vvk, vvk_scheme_after_cleaning, metric_info_list_dict)

    #SCH_VER
    if db.sch_ver_select_check_false():
        db.sch_ver_update_vvk_if_false(scheme_revision_vvk, user_query_interval_revision, vvk_scheme_after_cleaning, metric_info_list_dict)


    return vvk_scheme_after_cleaning
