import sys
import json

def open_json(name_file: str):
    with open(name_file, 'r', encoding='utf-8') as file:
        data = file.read()
    return json.loads(data)


def build_paths(templates_all, root_item, parent_path=""):
    paths = []

    if 'includes' in root_item:
        for item in root_item['includes']:
            for index in range(item['count']):
                str_path = f"{parent_path}/{item['template_id']}[{index}]"
                paths.append(str_path)

                # Найти соответствующий элемент в templates_all
                sub_item = next((i for i in templates_all if i['template_id'] == item['template_id']), None)
                if sub_item:
                    paths.extend(build_paths(templates_all, sub_item, str_path))

    return paths



try:
    join = open_json('json/1.json')
    agent1 = open_json('json/11.json')
    agent2 = open_json('json/12.json')
    agent3 = open_json('json/13.json')

    templatres_all = []
    for item in join['scheme']['templates']:
        templatres_all.append(item)

    for item in agent1['scheme']['templates']:
        templatres_all.append(item)

    for item in agent2['scheme']['templates']:
        templatres_all.append(item)

    for item in agent3['scheme']['templates']:
        templatres_all.append(item)


    root_item = next(item for item in templatres_all if item['template_id'] == 'VVK_Asyst')

    all_paths =[root_item['template_id']] + build_paths(templatres_all, root_item, root_item['template_id'])

    print(len(all_paths))
    for i in all_paths:
        print(i)


    return_path = open_json("json/ret.json")

    old_path = []
    for item in return_path['scheme']['item_id_list']:
        old_path.append(item['full_path'])
    print("-------------")
    print(len(old_path))

    # Элементы, которые есть в list1, но нет в list2
    unique_to_list1 = [item for item in all_paths if item not in old_path]

    # Элементы, которые есть в list2, но нет в list1
    unique_to_list2 = [item for item in old_path if item not in all_paths]

    print(f"Элементы, которые должны быть, но нет собранной схеме:")
    for i in unique_to_list1:
        print(i)
    print(f"Элементы, которые есть в собранной схеме, но нет в той, которая должна :")
    for i in unique_to_list2:
        print(i)
except Exception as e:
    sys.exit(1)