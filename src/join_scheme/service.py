from database.database import Database

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
                raise ValueError(
                    "Ошибка: Метрика с идентификатором '{}' уже существует, но имеет различные параметры".format(
                        item["metric_id"]))
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
                raise ValueError(
                    "Ошибка: Шаблон с идентификатором '{}' уже существует, но имеет различные параметры".format(
                        item["template_id"]))
        else:
            templates_list.append(item)
    return templates_list

# !!!
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

# !!!
def formation_agent_update_join(agent_scheme: dict, join_scheme: dict, vvk_scheme: dict):
    """
        Обновляет схему VVK на основе схемы агента и join схемы.

    Args:
        agent_scheme (dict): Схема агента, содержащая метрики, шаблоны, списки join_id, item_id и item_info.
        join_scheme (dict): Join схема, содержащая списки подключений и их типы.
        vvk_scheme (dict): Схема VVK, которую необходимо обновить.

    Returns:
        dict: Обновленная схема VVK.

    Raises:
        ValueError: Если возникают ошибки при добавлении метрик, шаблонов или проверке путей.
    """
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

                if agent_scheme["scheme"]["join_id_list"] is not None:
                    for item in agent_scheme["scheme"]["join_id_list"]:
                        full_path_item = join_list["join_item_full_path"] + '/' + item["full_path"]
                        if check_full_path_exists(join_scheme["item_id_list"], full_path_item):
                            raise ValueError(
                                f"При попытки регистрации агента по типу соединения 'jtInclude' не был найден путь в Jion: {full_path_item}")

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
                    raise ValueError("Разное количество join_id_list с JoinSheme")

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
                        raise ValueError("Нет '{}' в join_id_list".format(
                            join_id_list_scheme["agent_item_join_id"]))

    return vvk_scheme

# ___________ работа только с БД _________

# !!!
def registration_join_scheme(join_scheme: dict, db: Database) -> dict:
    """
        Регистрирует схему ВВК в базе данных и возвращает ее структуру в словаре.

    Args:
        join_scheme (dict): Словарь с информацией о схеме объединения.
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
    # GUI
    vvk_puth = join_scheme["scheme"]["item_id_list"][0]["full_path"].split("/")[0]
    vvk_name = [item for item in join_scheme["scheme"]["templates"] if item.get('template_id') == vvk_puth][0][
        "name"]
    agents_reg_id = [item["agent_reg_id"] for item in join_scheme["scheme"]["join_list"]]
    db.gui_insert_join_scheme(vvk_name, agents_reg_id)
    # REG_SCH
    db.reg_sch_insert_vvk(join_scheme["scheme_revision"], join_scheme["scheme"], vvk_scheme, None)
    return vvk_scheme

# !!!
def re_registration_join_scheme(join_scheme_new, user_query_interval_revision,
                                            metric_info_list_raw, db: Database) -> dict:
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
    item_id_list = []
    index = 0
    for a in join_scheme_new["scheme"]["item_id_list"]:
        item_id_list.append({"full_path": a["full_path"], "item_id": index})
        index += 1
    vvk_scheme_new["item_id_list"] = item_id_list

    # GUI
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
                    vvk_scheme_new = formation_agent_update_join(agent, join_scheme_new["scheme"], vvk_scheme_new)
                    db.gui_update_agent_reg_id_reg_true(agent["number_id"], agent["agent_reg_id"],
                                                        agent["scheme_revision"])
                except Exception as e:
                    db.gui_update_agent_reg_id_update_error(agent["number_id"], agent["agent_reg_id"],
                                                            agent["scheme_revision"], str(e))
            else:
                # !?! Необходимо дописать модуль, который будет чистить МетрикИнфо
                db.reg_sch_delete_agent(agent["number_id"])

    # GUI
    db.gui_update_vvk_reg_none(join_scheme_new["scheme_revision"], user_query_interval_revision)

    # REG
    db.reg_sch_update_vvk_scheme_all(join_scheme_new["scheme_revision"], join_scheme_new["scheme"], vvk_scheme_new)

    # SCH - случай когда ввк схема зарегистрированна!
    vvk_id = db.sch_ver_select_check_vvk_id()
    if vvk_id:
        if db.sch_ver_select_latest_status():
            db.sch_ver_insert_vvk(False, vvk_id, join_scheme_new["scheme_revision"], user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_raw)
        else:
            db.sch_ver_update_vvk_if_false(join_scheme_new["scheme_revision"], user_query_interval_revision,
                                  vvk_scheme_new, metric_info_list_raw)
            print("RERERERERERER")

    db.reg_sch_block_false()
    return vvk_scheme_new
