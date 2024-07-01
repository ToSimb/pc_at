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

    print("___________________")
    print("отправка ПФ - агент 1 - неуспешно!")
    subprocess.run(['python', 'test_pf_1_0.py'])
    time.sleep(T3)

    print("___________________")
    print("Регистрация агента 2")
    subprocess.run(['python', 'test_reg_agent_2.py'])
    time.sleep(T3)
    #
    print("___________________")
    print("Регистрация ВВК схемы")
    subprocess.run(['python', 'test_reg_vvk.py'])
    time.sleep(T3)
    #
    print("___________________")
    print("Проверка контроля связи для всех агентов")
    subprocess.run(['python', 'test_check_agents.py'])
    time.sleep(T3)

    print("___________________")
    print("отправка ПФ - агент 1")
    subprocess.run(['python', 'test_pf_1_0.py'])
    time.sleep(T3)

    print("___________________")
    print("отправка ПФ - агент 2")
    subprocess.run(['python', 'test_pf_2_0.py'])
    time.sleep(T3)

    print("___________________")
    print("Проверка контроля связи ВВК")
    subprocess.run(['python', 'test_check_norm.py'])
    time.sleep(T3)
    #
    print("___________________")
    print("Проверка контроля связи ВВК - 227 -  с обновлением Metric_info")
    subprocess.run(['python', 'test_check_227.py'])
    time.sleep(T3)

    print("___________________")
    print("Включение режима для сохранения последних ПФ")
    subprocess.run(['python', 'test_save_status.py'])
    time.sleep(T3)

    print("___________________")
    print("отправка ПФ - агент 1")
    subprocess.run(['python', 'test_pf_1_0.py'])
    time.sleep(T3)

    print("___________________")
    print("отправка ПФ - агент 2")
    subprocess.run(['python', 'test_pf_2_0.py'])
    time.sleep(T3)

    print("___________________")
    print("Выключение режима для сохранения последних ПФ")
    subprocess.run(['python', 'test_save_status.py'])
    time.sleep(T3)

    print("___________________")
    print("Перерегистрация агента 2 - неудачно")
    subprocess.run(['python', 'test_reg_agent_2_false.py'])
    time.sleep(T3)

    print("___________________")
    print("Перерегистрация JoinScheme 2")
    subprocess.run(['python', 'test_re_reg_join.py'])
    time.sleep(T3)

    # # НЕ СТОИТ ДЕЛАТЬ - ОТРАБОТАНО
    # print("___________________")
    # print("Перерегистрация JoinScheme 2 - one_agents")
    # subprocess.run(['python', 'test_re_reg_join_scheme_one_agents.py'])
    # time.sleep(T3)

    print("___________________")
    print("Перерегистрация агента 2 - удачно")
    subprocess.run(['python', 'test_re_reg_agent_2.py'])
    time.sleep(T3)

    print("___________________")
    print("Перерегистрация ВВК схемы")
    subprocess.run(['python', 'test_re_reg_vvk.py'])
    time.sleep(T3)

    # subprocess.run(['python', 'test_re_reg_join_old.py'])
    # time.sleep(T3)
except Exception as e:
    print(e)