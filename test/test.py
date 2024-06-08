import subprocess
import time

try:
    subprocess.run(['python', 'test_create_table.py'])
    time.sleep(15)
    subprocess.run(['python', 'test_reg_join_scheme.py'])
    time.sleep(15)
    subprocess.run(['python', 'test_reg_agent_1.py'])
    time.sleep(15)
    subprocess.run(['python', 'test_reg_agent_2.py'])
    time.sleep(15)
    subprocess.run(['python', 'test_reg_agent_2_false.py'])
    time.sleep(15)
    subprocess.run(['python', 'test_re_reg_join.py'])
    time.sleep(15)
    subprocess.run(['python', 'test_re_reg_agent_2.py'])
    time.sleep(15)
    subprocess.run(['python', 'test_re_reg_join_old.py'])
    time.sleep(15)
except Exception as e:
    print(e)