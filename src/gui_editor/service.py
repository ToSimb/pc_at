import json

from myException import MyException427

from database.database import Database

from logger.logger import logger


def if_metric_info(metric_info: dict) -> list:
    """
    Возвращает 'metric_info_list' из словаря metric_info, если оно существует.

    Args:
        metric_info (dict): Словарь, содержащий ключ 'metric_info_list', значение которого будет проверено.

    Returns:
        list: Список, содержащий значение по ключу 'metric_info_list', или пустой список, если значение отсутствует или некорректно.
    """
    if metric_info is None:
        return []

    metric_info_list = metric_info.get('metric_info_list')

    if not metric_info_list or metric_info_list == [None]:
        return []

    return metric_info_list

def load_new_vvk_cheme(new_scheme_vvk: dict, db: Database):
    if db.reg_sch_block_check():
        raise BlockingIOError
    db.reg_sch_block_true()

    # GUI
    vvk_puth = new_scheme_vvk["scheme"]["item_id_list"][0]["full_path"].split("/")[0]
    vvk_name = [item for item in new_scheme_vvk["scheme"]["templates"] if item.get('template_id') == vvk_puth][0]["name"]
    db.gui_update_vvk_name(vvk_name)

    # GUI
    db.gui_update_vvk_reg_none(new_scheme_vvk["scheme_revision"], new_scheme_vvk["scheme_revision"])
    metric_info_list_raw = {
        "metric_info_list": new_scheme_vvk["metric_info_list"]
    }
    # REG
    db.reg_sch_update_vvk_scheme_from_editor(new_scheme_vvk["scheme_revision"], new_scheme_vvk["scheme"], metric_info_list_raw)

    # SCH - случай когда ввк схема зарегистрирована!
    vvk_id = db.sch_ver_select_check_vvk_id()
    if vvk_id:
        if db.sch_ver_select_latest_status():
            db.sch_ver_insert_vvk(False, vvk_id, new_scheme_vvk["scheme_revision"], new_scheme_vvk["user_query_interval_revision"],
                                  new_scheme_vvk["scheme"], metric_info_list_raw)
        else:
            db.sch_ver_update_vvk_if_false(new_scheme_vvk["scheme_revision"], new_scheme_vvk["user_query_interval_revision"],
                                  new_scheme_vvk["scheme"], metric_info_list_raw)
    db.reg_sch_block_false()