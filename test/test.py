import subprocess
import time

T3 = 1

try:
    subprocess.run(['python', 'test_create_table.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_reg_join_scheme.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_reg_agent_1.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_reg_agent_2.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_check_norm.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_check_227.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_reg_agent_2_false.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_re_reg_join.py'])
    time.sleep(T3)
    subprocess.run(['python', 'test_re_reg_agent_2.py'])
    time.sleep(T3)
    # subprocess.run(['python', 'test_re_reg_join_old.py'])
    # time.sleep(T3)
except Exception as e:
    print(e)