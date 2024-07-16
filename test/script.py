
import json

def save_to_json(data):
    filename = f"12212.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

mass = []



str = "chassis_0_FREON51CN"

for i in range(1, 10):
    str_i = f"{str}0{i}"
    a = {
        "template_id": str_i,
        "name": str_i,
        "description":str_i
    }
    mass.append(a)

for i in range(10, 81):
    str_i = f"{str}{i}"
    a ={
        "template_id": str_i,
        "name": str_i,
        "description":str_i
    }
    mass.append(a)

save_to_json(mass)

