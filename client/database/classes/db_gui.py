import datetime

from logger.logger import logger


class Gui:

# ______________ GUI _______________

# __ Create Table __
    def gui_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS gui (
                    id SERIAL PRIMARY KEY,
                    vvk_name VARCHAR(50),
                    type_id BOOLEAN DEFAULT TRUE,
                    number_id INT,
                    agent_reg_id VARCHAR(30),
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    status_reg BOOLEAN,
                    time_reg TIMESTAMP,
                    error_reg VARCHAR(250),
                    time_value TIMESTAMP,
                    error_value VARCHAR(250),
                    time_conn TIMESTAMP,
                    error_conn BOOLEAN DEFAULT FALSE
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(gui): таблица создана")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_create_table: %s", e)
            raise e

# __ Drop Table __
    def gui_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS gui;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(gui): таблица удалена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_drop_table: %s", e)
            raise e

# __ Select __
    # !!!
    def gui_select_agents_reg(self) -> tuple:
        """
            SQL-запрос на получение идентификаторов и регистрационных идентификаторов агентов.

        Returns:
            tuple: Кортеж, содержащий списки идентификаторов агентов и их регистрационных идентификаторов.
                   Первый элемент кортежа содержит список number_id, второй - список agent_reg_id.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select_agent_reg_id = "SELECT number_id, agent_reg_id FROM gui WHERE type_id = TRUE;"
            cur.execute(sql_select_agent_reg_id)
            rows = cur.fetchall()
            number_id = [row[0] for row in rows if row[0] is not None]
            agent_reg_id = [row[1] for row in rows]
            self.conn.commit()
            return number_id, agent_reg_id
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_select_agents_reg: %s", e)
            raise e

    # !!!
    def gui_select_agents_check_status_reg(self) -> bool:
        """
            SQL-запрос на проверку значений колонки status_reg для агентов.

        Returns:
            bool: True, если все значения в колонке status_reg равны TRUE, иначе False.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_check_status_reg = "SELECT status_reg FROM gui WHERE type_id = TRUE;"
            cur.execute(sql_check_status_reg)
            rows = cur.fetchall()
            all_status_true = all(row[0] for row in rows)
            self.conn.commit()
            return all_status_true
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_check_status_reg: %s", e)
            raise e
# __ Insert __

# __ Update __
    # !!!
    def gui_update_vvk_reg_error(self, error_reg: str) -> bool:
        """
            SQL-запрос: Обновляет таблицу GUI с информацией об ошибке регистрации ВВК.

        Args:
            error_reg (str): Описание ошибки регистрации.

        Returns:
            bool: True, если функция выполнена успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET status_reg = %s, time_reg = %s, error_reg = %s WHERE type_id = FALSE;"
            cur.execute(sql_update_gui, (False, time_reg, error_reg))
            self.conn.commit()
            logger.error(f"DB(gui): {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_vvk_reg_error: %s", e)
            raise e

    def gui_update_vvk_reg_true(self, vvk_id: int, scheme_revision: int, user_query_interval_revision: int) -> bool:
        """
            SQL-запрос: Обновляет таблицу GUI после успешной регистрации VVK.

        Args:
            vvk_id (int): Идентификатор зарегистрированной VVK.
            scheme_revision (str): Версия схемы.
            user_query_interval_revision (str): Версия интервала запроса пользователя.

        Returns:
            bool: Возвращает True, если обновление таблицы выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = ("UPDATE gui SET number_id = %s, scheme_revision = %s, user_query_interval_revision = %s, "
                              "status_reg = %s, time_reg = %s, error_reg = %s "
                              "WHERE type_id = FALSE;")
            cur.execute(sql_update_gui,
                        (vvk_id, scheme_revision, user_query_interval_revision, True, time_reg, None))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_vvk_reg_true - vvk_id %s : %s", vvk_id, e)
            raise e


    # !!!
    def gui_update_value(self, agent_id: int, error_value: str, type_id: bool) -> bool:
        """
            SQL-запрос на обновление статуса передачи ПФ.

        Args:
            agent_id (int): Идентификатор агента или VVK.
            error_value (str): Значение ошибки, если она есть.
            type_id (bool): Тип агента. True - агент, False - VVK.

        Returns:
            bool: Возвращает True, если обновление успешно выполнено.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_value = %s, error_value = %s WHERE number_id = %s AND type_id = %s;"
            cur.execute(sql_update_gui, (time_reg, error_value, agent_id, type_id))
            self.conn.commit()
            if error_value:
                if type_id:
                    logger.error(f"DB(gui): ошибка приема ПФ agent_id '{agent_id}': {error_value}")
                else:
                    logger.error(f"DB(gui): ошибка приема ПФ vvk_id '{agent_id}': {error_value}")
            return True
        except Exception as e:
            self.conn.rollback()
            if type_id:
                logger.error("DB(gui): gui_update_value - agent_id %s: %s", agent_id, e)
            else:
                logger.error("DB(gui): gui_update_value - vvk_id %s: %s", agent_id, e)
            raise e

    # !!!
    def gui_update_check_number_id(self, number_id: int, error_conn: bool) -> bool:
        """
            SQL-запрос на обновление последней проверки соединения агента/ВВК.

        Args:
            agent_id (int): Идентификатор агента.
            error_conn (bool): Состояние потери соединения.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_conn = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_conn = %s, error_conn = %s WHERE number_id = %s;"
            cur.execute(sql_update_gui, (time_conn, error_conn, number_id))
            self.conn.commit()
            if error_conn:
                logger.info(f"DB(gui): agent_id/VVk '{number_id}' - проверка связи не успешная")
            else:
                logger.info(f"DB(gui): agent_id/VVk '{number_id}' - проверка связи успешная")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_check_number_id - %s : %s", number_id, e)
            raise e

    # !!!
    def gui_update_all_user_query_revision(self, user_query_interval_revision: int) -> bool:
        """
            SQL-запрос: Обновляет версию интервала запроса пользователя в таблице gui для всех записей.

        Args:
            user_query_interval_revision (int): Новая версия интервала запроса пользователя.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE gui SET user_query_interval_revision = {user_query_interval_revision};"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(gui): значение user_query_interval_revision успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_all_user_query_revision: %s", e)
            raise e

# __ Delete __
    def gui_delete(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_delete = f"DELETE FROM gui;"
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info("DB(gui): таблица очищена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_delete: %s", e)
            raise e
