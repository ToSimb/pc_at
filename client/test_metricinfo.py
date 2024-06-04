import sys
import time
import random
import requests

def metric_info_if_value(Met):
    if Met is None:
        print('1. no metric_info_list')
        return None
    else:
        # надо написать функцию которая проверяет ключ!!
        if Met['metric_info_list'] is None:
            print('2. no metric_info_list')
            return None
        if Met['metric_info_list'] == []:
            print('3. no metric_info_list')
            return None
        if Met['metric_info_list'] == [None]:
            print('4. no metric_info_list')
            return None
        else:
            return Met['metric_info_list']
    return None

from database.postgres import connect, disconnect
from database.pf import Pf
from database.gui import Gui
from database.reg_sch import Reg_sch
from database.sch_ver import Sch_ver


conn = connect()
db_gui = Gui(conn)
db_pf = Pf(conn)
db_reg = Reg_sch(conn)
db_sch = Sch_ver(conn)


try:
    data = db_sch.sch_ver_select_vvk_reg_all_json()
    print('metric_info_list:', data['metric_info_list'])
    print("SSS  ", data['scheme_revision'])
    data1 = {
        "vvk_id": data["vvk_id"],
        "scheme_revision": data["scheme_revision"]+1,
        "user_query_interval_revision": data["user_query_interval_revision"]
    }

    Met = data['metric_info_list']
    M = metric_info_if_value(Met)

    print("!", M)

    met = {
        'metric_info_list': [{"a":12, "b": 12},{"a":12, "b": 12},{"a":12, "b": 12}]
    }

    db_sch.sch_ver_insert_vvk(True, data1, data["scheme"], met)

except Exception as e:
    print(e)
    disconnect(conn)
    sys.exit(1)