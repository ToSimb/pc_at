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
    print("Регистрация агента 2")
    subprocess.run(['python', 'test_reg_agent_2.py'])
    time.sleep(T3)

except Exception as e:
    print(e)