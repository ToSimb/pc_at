import subprocess
import time

T3 = 0

try:
    print("___________________")
    print("Создание таблиц")
    subprocess.run(['python', 'test_create_table.py'])
    time.sleep(T3)

    print("___________________")
    print("Загрузка JoinScheme 1")
    subprocess.run(['python', 'test_reg_join_scheme.py'])
    time.sleep(T3)

    print("___________________")
    print("Регистрация агента 1")
    subprocess.run(['python', 'test_reg_agent_1.py'])
    time.sleep(T3)

    # print("___________________")
    # print("отправка ПФ - агент 1 - неуспешно!")
    # subprocess.run(['python', 'test_pf_1_0.py'])
    # time.sleep(T3)

    print("___________________")
    print("Регистрация агента 2")
    subprocess.run(['python', 'test_reg_agent_2.py'])
    time.sleep(T3)
    #
    # print("___________________")
    # print("Регистрация ВВК схемы")
    # subprocess.run(['python', 'test_reg_vvk.py'])
    # time.sleep(T3)
    #
    # print("___________________")
    # print("Проверка контроля связи для всех агентов")
    # subprocess.run(['python', 'test_check_agents.py'])
    # time.sleep(T3)
    #
    # print("___________________")
    # print("отправка ПФ - агент 1")
    # subprocess.run(['python', 'test_pf_1_0.py'])
    # time.sleep(T3)
    #
    # print("___________________")
    # print("отправка ПФ - агент 2")
    # subprocess.run(['python', 'test_pf_2_0.py'])
    # time.sleep(T3)
    #
    # print("___________________")
    # print("Проверка контроля связи ВВК")
    # subprocess.run(['python', 'test_check_norm.py'])
    # time.sleep(T3)
    # #
    # print("___________________")
    # print("Проверка контроля связи ВВК - 227 -  с обновлением Metric_info")
    # subprocess.run(['python', 'test_check_227.py'])
    # time.sleep(T3)

except Exception as e:
    print(e)