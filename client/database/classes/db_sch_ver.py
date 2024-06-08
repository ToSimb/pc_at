import time
import json

from logger.logger import logger


class Sch_ver:

# ____________ SCH_VER _____________

# __ Create Table __
    def sch_ver_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS sch_ver (
                    id SERIAL PRIMARY KEY,
                    vvk_id INT,
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    date_create BIGINT,
                    t3 INT,
                    status_reg BOOLEAN DEFAULT FALSE,
                    scheme JSONB,
                    metric_info_list JSONB
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(sch_ver): таблица создана")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_create_table: %s", e)
            raise e

# __ Drop Table __
    def sch_ver_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS sch_ver;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(sch_ver): таблица удалена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_drop_table: %s", e)
            raise e

# __ Select __
    # !!!
    def sch_ver_select_vvk_details(self) -> tuple:
        """
            SQL-запрос: Получения деталей по зарегистрированной схему ВВК.

        Returns:
            tuple: Кортеж, содержащий vvk_id, scheme_revision, user_query_interval_revision и t3.
                   Если запись не найдена, возвращает кортеж из четырех элементов [None, None, None, None].

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = ("SELECT vvk_id, scheme_revision, user_query_interval_revision, t3 FROM sch_ver "
                          "WHERE status_reg = TRUE ORDER BY date_create DESC LIMIT 1")
            cur.execute(sql_select, )
            result = cur.fetchone()
            if result:
                return result
            else:
                return [None, None, None, None]
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_select_vvk_scheme: %s", e)
            raise e

    # !!!
    def sch_ver_select_date_create_unreg(self) -> int:
        """
            SQL-запрос: Получить время регистрации последней успешной зарегистрированной схемы ВВК.

        Returns:
            int: Значение date_create для первой найденной записи.
                 Если запись не найдена, возвращает None.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = (
                "SELECT date_create FROM sch_ver "
                "WHERE status_reg = FALSE "
                "ORDER BY date_create "
                "LIMIT 1"
            )
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_select_date_create: %s", e)
            raise e


    # возжно приходится !?!
    def sch_ver_select_date_create_unreg_old(self) -> int:
        try:
            cur = self.conn.cursor()
            sql_select = (
                "SELECT scheme_revision, date_create FROM sch_ver "
                "WHERE status_reg = FALSE "
                "ORDER BY date_create "
                "LIMIT 1"
            )
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result[0], result[1]
            else:
                return None, None
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_select_date_create: %s", e)
            raise e

    def sch_ver_select_vvk_details_unreg(self) -> tuple:
        """
            SQL-запрос: Извлекает детали незарегистрированной VVK.

        Returns:
            tuple: Кортеж с деталями незарегистрированной VVK, включая vvk_id, scheme_revision, scheme и metric_info_list.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = (
                "SELECT vvk_id, scheme_revision, scheme, metric_info_list FROM sch_ver "
                "WHERE status_reg = FALSE "
            )
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                return result
            else:
                return (None, None, None, None)
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_select_vvk_details_unreg: %s", e)
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
            logger.error("DB(sch_ver): sch_ver_insert_vvk_scheme: ошибка регистации vvk_scheme у AF: %s", e)
            raise e

# __ Update __
    # !!!
    def sch_ver_update_status_reg(self, scheme_revision: int) -> bool:
        """
            SQL-запрос: Обновляет статус регистрации схемы в таблице SCH_VER.

        Args:
            scheme_revision (int): Версия схемы, для которой обновляется статус регистрации.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно, иначе False.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_update = (
                "UPDATE sch_ver "
                "SET status_reg = TRUE "
                "WHERE scheme_revision = %s"
            )
            cur.execute(sql_update, (scheme_revision,))
            self.conn.commit()
            logger.info(f"DB(sch_ver): sch_ver_update_status_reg: {scheme_revision} : TRUE")
            return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_update_status_reg: ошибка обновления status_reg: %s", e)
            raise e

    # !!!
    def sch_ver_update_all_user_query_revision(self, user_query_interval_revision: int) -> bool:
        """
            SQL-запрос: Обновляет версию интервала запроса пользователя в таблице SCH_VER для всех записей.

        Args:
            user_query_interval_revision (int): Новая версия интервала запроса пользователя.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE sch_ver SET user_query_interval_revision = {user_query_interval_revision};"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(sch_ver): значение user_query_interval_revision успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_update_all_user_query_revision: %s", e)
            raise e

# __ Delete __

    def sch_ver_delete_vvk_no_reg(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete = (
                "DELETE FROM sch_ver "
                "WHERE ctid = (SELECT ctid FROM sch_ver WHERE status_reg = FALSE ORDER BY date_create LIMIT 1);"
            )
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info(f"DB(sch_ver): Удалена не удачная версия Vvk Scheme")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): sch_ver_delete_vvk_no_reg: %s", e)
            raise e











    def sch_ver_select_vvk_reg_all_json(self) -> dict:
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT vvk_id, scheme_revision, user_query_interval_revision, scheme, metric_info_list FROM sch_ver WHERE status_reg = TRUE ORDER BY id DESC LIMIT 1"
            cur.execute(sql_select, )
            self.conn.commit()
            data = cur.fetchall()
            result = {
                "vvk_id": data[0][0],
                "scheme_revision": data[0][1],
                "user_query_interval_revision": data[0][2],
                "scheme": data[0][3],
                "metric_info_list": data[0][4]
            }
            if result:
                return result
            else:
                raise Exception("VvkScheme не зарегистирована!!")
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): sch_ver_select_vvk_reg_all_json: %s", e)
            raise e

