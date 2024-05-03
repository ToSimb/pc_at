import os
import json
import fcntl
import time
import requests

from logger.logger import logger

def open_json(name_file: str):
    # Открытие JoinAgents
    with open(name_file, 'r', encoding='utf-8') as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        data = file.read()
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)
    # Преобразование JSON в словарь
    json_data = json.loads(data)
    return json_data

def agents(agent_reg_id: str):
    try:
        agents = open_json("registration/json/agents.json")
        if agent_reg_id in agents:
            return agents[agent_reg_id]
        index = max(agents.values())
        index += 1
        agents[agent_reg_id] = index
        with open("registration/json/agents.json", 'w', encoding='utf-8') as file1:
            json.dump(agents, file1, ensure_ascii=False)
        return index
    except FileNotFoundError:
        agents = {agent_reg_id: 1}
        with open("registration/json/agents.json", 'w', encoding='utf-8') as file1:
            json.dump(agents, file1, ensure_ascii=False)
        return 1

def create_json_vvk(json_join_scheme: dict):
    # Записываем JoinScheme в фал
    with open("registration/json/join_scheme.json", 'w', encoding='utf-8') as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Формируем структуру VvkScheme
        json_vvk_return = {
            "scheme_revision": json_join_scheme["scheme_revision"],
            "scheme": {
                "metrics": [],
                "templates": json_join_scheme["scheme"]["templates"],
                "item_id_list": [],
                "item_info_list": json_join_scheme["scheme"]["item_info_list"]
            }
        }
        # Создаем пустой список и индекс для формирования item_id_list
        item_id_list = []
        index = 0
        # формирования списка с item_id_list
        for a in json_join_scheme["scheme"]["item_id_list"]:
            item_id_list.append({"full_path": a["full_path"], "item_id": index})
            index += 1
        # Добавление item_id_list в json
        json_vvk_return["scheme"]["item_id_list"] = item_id_list
        # Записать VvkScheme в файл
        with open("registration/json/vvk_scheme.json", 'w', encoding='utf-8') as file1:
            fcntl.flock(file1.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            json.dump(json_vvk_return, file1, ensure_ascii=False)
            fcntl.flock(file1.fileno(), fcntl.LOCK_UN)
        # Сохраняем данные
        json.dump(json_join_scheme, file, ensure_ascii=False)
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

def add_metrics(json_vvk_return_metrics, json_agent_scheme_metrics):
    metrics_list = []
    for item in json_agent_scheme_metrics:
        existing_metric = next(
            (metric for metric in json_vvk_return_metrics if metric["metric_id"] == item["metric_id"]),
            None)
        if existing_metric:
            if existing_metric == item:
                metrics_list.append(item)
            else:
                raise ValueError(
                    "Ошибка: Метрика с идентификатором '{}' уже существует, но имеет различные параметры".format(
                        item["metric_id"]))
        else:
            metrics_list.append(item)
    return metrics_list

def add_templates(json_vvk_return_templates, json_agent_scheme_templates):
    templates_list = []
    for item in json_agent_scheme_templates:
        existing_template = next((template for template in json_vvk_return_templates if
                                  template["template_id"] == item["template_id"]), None)
        if existing_template:
            if existing_template == item:
                templates_list.append(item)
            else:
                raise ValueError(
                    "Ошибка: Шаблон с идентификатором '{}' уже существует, но имеет различные параметры".format(
                        item["template_id"]))
        else:
            templates_list.append(item)
    return templates_list

def add_json_vvk(json_agent_scheme: dict, agent_reg_id: str):
    json_join_scheme = open_json("registration/json/join_scheme.json")
    with open("registration/json/vvk_scheme.json", 'r+', encoding='utf-8') as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        json_vvk_return = json.load(file)


        json_agent_list = []
        agent_found = False
        for join_list in json_join_scheme["scheme"]["join_list"]:
            if agent_reg_id == join_list["agent_reg_id"]:
                agent_found = True
                # если тип подключения jtInclude
                if join_list["join_type"] == "jtInclude":
                    try:
                        # проверка и добавление metrics
                        json_vvk_return['scheme']['metrics'] = add_metrics(json_vvk_return['scheme']['metrics'],
                                                                       json_agent_scheme['scheme']['metrics'])
                        # проверка и добавление templates
                        json_vvk_return['scheme']['templates'] = add_templates(json_vvk_return['scheme']['templates'],
                                                                           json_agent_scheme['scheme']['templates'])
                    except ValueError as e:
                        print(e)
                        raise ValueError(e)

                    # поиск самого большого item_id
                    if json_vvk_return["scheme"]["item_id_list"]:
                        index = max(
                            item['item_id'] for item in json_vvk_return["scheme"]["item_id_list"] if 'item_id' in item)
                    else:
                        index = 0
                    # Формирование нового item_id_list
                    for a in json_agent_scheme["scheme"]["item_id_list"]:
                        index += 1
                        a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
                        a["item_id"] = index
                        for existing_item in json_vvk_return["scheme"]["item_id_list"]:
                            if existing_item["full_path"] == a["full_path"]:
                                existing_item["item_id"] = a["item_id"]
                                break
                        else:
                            json_vvk_return["scheme"]["item_id_list"].append(a)
                        json_agent_list.append(a)
                    # Формирование нового item_info_list
                    for a in json_agent_scheme["scheme"]["item_info_list"]:
                        a["full_path"] = join_list["join_item_full_path"] + '/' + a["full_path"]
                        b = next(
                            (b for b in json_vvk_return["scheme"]["item_info_list"] if
                             b["full_path"] == a["full_path"]),
                            None)
                        if b:
                            b.update(a)
                        else:
                            json_vvk_return["scheme"]["item_info_list"].append(a)

                # если тип подключения jtExclude
                if join_list["join_type"] == "jtAssign":
                    # проверка и добавление metrics
                    json_vvk_return['scheme']['metrics'] = add_metrics(json_vvk_return['scheme']['metrics'],
                                                                       json_agent_scheme['scheme']['metrics'])
                    # проверка и добавление templates
                    json_vvk_return['scheme']['templates'] = add_templates(json_vvk_return['scheme']['templates'],
                                                                           json_agent_scheme['scheme']['templates'])

                    if len(join_list["joins"]) != len(json_agent_scheme["scheme"]["join_id_list"]):
                        raise ValueError("Ошибка: разное количество join_id_list с JoinSheme")

                    # проходимся по join_id_list в json_agent_scheme
                    for join_id_list_scheme in join_list["joins"]:
                        join_id_list_agent = next(
                            (join_id_list_agent for join_id_list_agent in json_agent_scheme["scheme"]["join_id_list"]
                             if join_id_list_scheme["agent_item_join_id"] == join_id_list_agent["join_id"]), None)
                        if join_id_list_agent:

                            # поиск самого большого item_id
                            if json_vvk_return["scheme"]["item_id_list"]:
                                index = max(
                                    item['item_id'] for item in json_vvk_return["scheme"]["item_id_list"] if
                                    'item_id' in item)
                            else:
                                index = 0

                            # формирование списка item_id_list
                            for a in json_agent_scheme["scheme"]["item_id_list"]:
                                if a["full_path"].split('/')[0] == join_id_list_agent["full_path"]:
                                    a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                        "full_path"].replace(
                                        a["full_path"].split('/')[0], "")
                                    index += 1
                                    a["item_id"] = index
                                    for existing_item in json_vvk_return["scheme"]["item_id_list"]:
                                        if existing_item["full_path"] == a["full_path"]:
                                            existing_item["item_id"] = a["item_id"]
                                            break
                                    else:
                                        json_vvk_return["scheme"]["item_id_list"].append(a)
                                    json_agent_list.append(a)

                            # формирование списка item_info_list
                            for a in json_agent_scheme["scheme"]["item_info_list"]:
                                if a["full_path"] == join_id_list_agent["full_path"]:
                                    a["full_path"] = join_id_list_scheme["join_item_full_path"] + a[
                                        "full_path"].replace(
                                        a["full_path"].split('/')[0], "")
                                    b = next(
                                        (b for b in json_vvk_return["scheme"]["item_info_list"] if
                                         b["full_path"] == a["full_path"]),
                                        None)
                                    if b:
                                        b.update(a)
                                    else:
                                        json_vvk_return["scheme"]["item_info_list"].append(a)

                        else:
                            raise ValueError("Ошибка: нет join_id:{} в join_id_list".format(
                                join_id_list_scheme["agent_item_join_id"]))

        if not agent_found:
            raise ValueError(
                "Ошибка: такого агента с ID {} не найдено".format(agent_reg_id))

        # котроль ahent_id
        index = agents(agent_reg_id)

        json_agent_return = {
            "agent_id": index,
            "item_id_list": json_agent_list
        }

        name_json = "registration/json/agent_" + str(index) + ".json"
        with open(name_json, 'w', encoding='utf-8') as file1:
            json.dump(json_agent_return, file1, ensure_ascii=False)

        file.seek(0)
        json.dump(json_vvk_return, file, ensure_ascii=False)
        file.truncate()
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

        return json_agent_return

def save_json_vvk(url: str, json_vvk_return: dict):
    headers = {'Content-Type': 'application/json'}
    try:
        logger.info(f"Отправка: {url}")
        response = requests.post(url, json=json_vvk_return, headers=headers)
        if response.status_code == 200:
            logger.info("Успушная регистрация")
            return response.json()
        else:
            logger.error(f"Произошла ошибка: {response.status_code}")
            logger.error(f"Произошла ошибка: {response.text}")
            return response.json()
    except requests.RequestException as e:
        logger.error(f"Произошла ошибка при регистрации: {e}")
        raise ValueError(e)





