import time
import json

from logger.logger import logger


class Sch_ver:
    # ____________ SCH_VER _____________

    # __ Select __
    # !!!
    def sch_ver_select_check_vvk_id(self) -> int:
        """
            SQL-запрос, который проверяет наличие идентификатора VVK и возвращает его, если запись найдена.

        Returns:
            int: Идентификатор VVK, если запись найдена, иначе возвращается False.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = ("SELECT vvk_id FROM sch_ver "
                          "WHERE status_reg = TRUE ORDER BY date_create DESC LIMIT 1")
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): get_latest_status: %s", e)
            raise e

    # !!!
    def sch_ver_select_latest_status(self) -> bool:
        """
            SQL-запрос для получения статуса последней версии схемы.

        Returns:
            bool: Если последний статус версии схемы 'True' возвращает True, иначе False.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = (
                "SELECT status_reg FROM sch_ver "
                "ORDER BY id DESC "
                "LIMIT 1"
            )
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): get_latest_status: %s", e)
            raise e

    # __ Insert __
    # !!!
    def sch_ver_insert_vvk(self, status_reg: bool, vvk_id: int, scheme_revision: int, user_query_interval_revision: int,
                           scheme: dict, metric_info_list: dict) -> bool:
        """
            SQL-запрос на новую запись зарегистрированной схемы ВВК в таблицу 'sch_ver'.

        Args:
            status_reg (bool): Флаг, указывающий, является ли это первая регистрация VVK.
            vvk_id (int): Идентификатор VVK.
            scheme_revision (int): Ревизия схемы.
            user_query_interval_revision (int): Ревизия интервала пользовательских запросов.
            scheme (dict): Схема VVK.
            metric_info_list (dict): Список информации о метриках.

        Returns:
            bool: Возвращает True, если регистрация прошла успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            current_time = int(time.time())
            cur = self.conn.cursor()
            sql_create = (
                "INSERT INTO sch_ver (vvk_id, scheme_revision, user_query_interval_revision, date_create, status_reg, scheme, metric_info_list) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s);")
            cur.execute(sql_create, (vvk_id, scheme_revision, user_query_interval_revision,
                                     current_time, status_reg, json.dumps(scheme), json.dumps(metric_info_list)))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_insert_vvk_scheme: %s", e)
            raise e


    # !!!
    def sch_ver_update_vvk_if_false(self, scheme_revision: int, user_query_interval_revision: int,
                                           scheme: dict, metric_info_list: dict) -> bool:
        """
            SQL-запрос для обновления записи незарегистрированной схемы ВВК.

        Args:
            scheme_revision (int): Ревизия схемы.
            user_query_interval_revision (int): Ревизия интервала пользовательских запросов.
            scheme (dict): Схема VVK.
            metric_info_list (dict): Список информации о метриках.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            current_time = int(time.time())
            cur = self.conn.cursor()
            sql_update = (
                "UPDATE sch_ver SET scheme_revision = %s, user_query_interval_revision = %s, date_create = %s, "
                "scheme = %s, metric_info_list = %s "
                "WHERE status_reg = %s;")
            cur.execute(sql_update, (scheme_revision, user_query_interval_revision, current_time,
                                     json.dumps(scheme), json.dumps(metric_info_list), False))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_update_vvk_if_false: %s", e)
            raise e