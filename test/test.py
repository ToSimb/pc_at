import subprocess
import time

T3 = 0

try:
    print("___________________")
    print("Создание таблиц")
    subprocess.run(['python', 'z_test_create_table.py'])
    time.sleep(T3)

    print("___________________")
    print("Загрузка JoinScheme 1")
    subprocess.run(['python', 'z_test_reg_join_scheme.py'])
    time.sleep(T3)

    print("___________________")
    print("Регистрация агента 1")
    subprocess.run(['python', 'z_test_reg_agent_1.py'])
    time.sleep(T3)
    #
    print("___________________")
    print("Регистрация агента 2")
    subprocess.run(['python', 'z_test_reg_agent_2.py'])
    time.sleep(T3)

    print("___________________")
    print("Регистрация ВВК схемы")
    subprocess.run(['python', 'z_test_reg_vvk.py'])
    time.sleep(T3)

    # print("___________________")
    # print("Загрузка новой JoinScheme 1")
    # subprocess.run(['python', 'z_test_reg_join_scheme_change_of_paths.py'])
    # time.sleep(T3)


except Exception as e:
    print(e)