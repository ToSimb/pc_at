import datetime

from logger.logger import logger


class Gui:

    # ______________ GUI _______________
    # __ Select __
    def gui_select_agents_reg(self) -> tuple:
        """
            SQL-запрос на получение идентификаторов и регистрационных идентификаторов агентов.

        Returns:
            tuple: Кортеж, содержащий number_id, agent_reg_id.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select_agent_reg_id = "SELECT number_id, agent_reg_id FROM gui WHERE type_id = TRUE;"
            cur.execute(sql_select_agent_reg_id)
            rows = cur.fetchall()
            number_id = [int(row[0]) for row in rows if row[0] is not None]
            agent_reg_id = [row[1] for row in rows]
            self.conn.commit()
            return number_id, agent_reg_id
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_select_agents_reg: %s", e)
            raise e

    def gui_select_check_agent_reg_id(self, agent_reg_id: str) -> bool:
        """
            Проверяет наличие записи с указанным 'agent_reg_id' в базе данных.

        Args:
            agent_reg_id (str): Идентификатор агента, по которому производится поиск.

        Returns:
            bool: True, если запись существует, False в противном случае.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            with self.conn.cursor() as cur:
                sql_select_check = """
                    SELECT COUNT(*) FROM gui WHERE type_id = TRUE AND agent_reg_id = %s;
                """
                cur.execute(sql_select_check, (agent_reg_id,))
                result = cur.fetchone()[0]
                self.conn.commit()
                return result > 0
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_select_check_agent_reg_id: %s", e)
            raise e

    def gui_select_agent_id_for_check_agent_reg_id(self, agent_reg_id: str) -> int:
        """
            SQL-запрос для получения 'number_id' агента.

        Args:
            agent_reg_id (str): Идентификатор агента, по которому производится поиск.

        Returns:
            int: 'number_id' найденной записи.

        Raises:
            Exception: Если запись с указанным 'agent_reg_id' не найдена или содержит пустое значение.
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            with self.conn.cursor() as cur:
                sql_select_check = """
                    SELECT number_id FROM gui WHERE type_id = TRUE AND agent_reg_id = %s;
                """
                cur.execute(sql_select_check, (agent_reg_id,))
                result = cur.fetchone()
                self.conn.commit()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_select_agent_id_for_check_agent_reg_id: %s", e)
            raise e

    def gui_select_check_agent_status_reg(self, number_id: int) -> bool:
        """
            SQL-запрос на проверку регистрации агента.

        Args:
            number_id (int): Идентификатор агента.

        Returns:
            bool: True, если агент зарегистрирован, иначе False.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select_check = "SELECT status_reg FROM gui WHERE number_id = %s and type_id = TRUE;"
            cur.execute(sql_select_check, (number_id,))
            result = cur.fetchone()
            self.conn.commit()
            if result:
                return True
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_select_check_agent_status_reg: %s", e)
            raise e


    # __ Insert __
    def gui_insert_join_scheme(self, vvk_name: str, agents_reg_id: list):
        """
            SQL-запросы для вставки имени ВВК и идентификаторов агентов.

        Args:
            vvk_name (str): Имя ВВК для вставки в таблицу 'gui'.
            agents_reg_id (list): Список идентификаторов агентов для вставки в таблицу 'gui'.

        Returns:
            bool: Возвращает True, если операция прошла успешно, иначе выбрасывается исключение.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_insert1 = "INSERT INTO gui (vvk_name, type_id) VALUES (%s,%s);"
            cur.execute(sql_insert1, (vvk_name, False))
            sql_insert2 = "INSERT INTO gui (agent_reg_id) VALUES (%s);"
            cur.executemany(sql_insert2, [(agent_id,) for agent_id in agents_reg_id])
            self.conn.commit()
            logger.info("DB(gui): JoinScheme загружена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_insert_join_scheme: %s", e)
            raise e

    def gui_insert_agents(self, agents_reg_id: list):
        """
            SQL-запросы для вставки идентификаторов агентов.

        Args:
            agents_reg_id (list): Список идентификаторов агентов для вставки в таблицу 'gui'.

        Returns:
            bool: Возвращает True, если операция прошла успешно, иначе выбрасывается исключение.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_insert = "INSERT INTO gui (agent_reg_id) VALUES (%s);"
            cur.executemany(sql_insert, [(agent_id,) for agent_id in agents_reg_id])
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_insert_agents: %s", e)
            raise e

    # __ Update _
    def gui_update_agent_reg_id_error(self, agent_reg_id: str, error_reg: str) -> bool:
        """
            SQL-запрос: Обновляет информацию об ошибке регистрации агента.

        Args:
            agent_reg_id (str): Регистрационный идентификатор агента.
            error_reg (str): Ошибка, связанная с агентом.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_reg = %s, error_reg = %s WHERE agent_reg_id = %s;"
            cur.execute(sql_update_gui, (time_reg, error_reg, agent_reg_id))
            self.conn.commit()
            logger.error(f"DB(gui):  agent_reg_id '{agent_reg_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_reg_id_error - agent_reg_id %s : %s", agent_reg_id, e)
            raise e

    def gui_update_agent_reg_id_update_error(self, agent_id: int, agent_reg_id: str,
                                             scheme_revision: int, error_reg: str) -> bool:
        """
            SQL-запрос: Обновляет информацию об ошибке регистрации агента во время обновления JoinScheme.

        Args:
            agent_id (int): Идентификатор агента.
            agent_reg_id (str): Регистрационный идентификатор агента.
            scheme_revision (int): Ревизия схемы
            error_reg (str): Ошибка, связанная с агентом.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = ("UPDATE gui SET number_id = %s, scheme_revision = %s, status_reg = FALSE, time_reg = %s, error_reg = %s "
                              "WHERE agent_reg_id = %s;")
            cur.execute(sql_update_gui, (agent_id, scheme_revision, time_reg, error_reg, agent_reg_id))
            self.conn.commit()
            logger.error(f"DB(gui):  agent_reg_id '{agent_reg_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_reg_id_error - agent_reg_id %s : %s", agent_reg_id, e)
            raise e

    def gui_update_agent_id_error(self, agent_id: int, error_reg: str) -> bool:
        """
            SQL-запрос: Обновляет информацию об ошибке регистрации агента.

        Args:
            agent_id (int): Идентификатор агента.
            error_reg (str): Ошибка, связанная с агентом.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_reg = %s, error_reg = %s WHERE number_id = %s AND type_id = TRUE;"
            cur.execute(sql_update_gui, (time_reg, error_reg, agent_id))
            self.conn.commit()
            logger.error(f"DB(gui): agent_id '{agent_id}' ошибка: {error_reg}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_id_error - agent_id %s : %s", agent_id, e)
            raise e

    def gui_update_agent_id_tru(self, agent_id: int) -> bool:
        """
            SQL-запрос: Обновляет информацию об ошибке регистрации агента.

        Args:
            agent_id (int): Идентификатор агента.
            error_reg (str): Ошибка, связанная с агентом.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_reg = %s, error_reg = %s WHERE number_id = %s AND type_id = TRUE;"
            cur.execute(sql_update_gui, (time_reg, None, agent_id))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_id_error - agent_id %s : %s", agent_id, e)
            raise e

    def gui_update_agent_reg_id_reg_true(self, agent_id: int, agent_reg_id: str, scheme_revision: int) -> bool:
        """
            SQL-запрос на обновление статуса успешной регистрации агента.

        Args:
            agent_id (int): Идентификатор агента.
            agent_reg_id (str): Регистрационный идентификатор агента.
            scheme_revision (int): Ревизия схемы.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = """UPDATE gui 
                                SET number_id = %s, scheme_revision = %s, status_reg = %s, time_reg = %s, error_reg = %s 
                                WHERE agent_reg_id = %s;"""
            cur.execute(sql_update_gui, (agent_id, scheme_revision, True, time_reg, None, agent_reg_id))
            self.conn.commit()
            logger.info(f"DB(gui): agent_reg_id '{agent_reg_id}' успешно зарегистрирован.")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_reg_id_reg_true - agent_reg_id %s : %s", agent_reg_id, e)
            raise e

    def gui_update_agent_id_re_reg_true(self, agent_id: int, scheme_revision: int) -> bool:
        """
            SQL-запрос на обновление статуса успешной перерегистрации агента.

        Args:
            agent_id (int): Идентификатор агента.
            scheme_revision (int): Ревизия схемы.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = ("UPDATE gui SET scheme_revision = %s, status_reg = %s, time_reg = %s, error_reg = %s "
                              "WHERE number_id = %s AND type_id = TRUE;")
            cur.execute(sql_update_gui, (scheme_revision, True, time_reg, None, agent_id))
            self.conn.commit()
            logger.info(f"DB(gui): agent_id '{agent_id}' успешно перерегистрирован")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_id_reg_true - agent_id %s : %s", agent_id, e)
            raise e

    def gui_update_agent_check_number_id_tru(self, number_id: int) -> bool:
        """
            SQL-запрос на обновление успешной последней проверки соединения агента.

        Args:
            number_id (int): Идентификатор агента.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_conn = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            sql_update_gui = "UPDATE gui SET time_conn = %s, error_conn = %s WHERE number_id = %s and type_id = TRUE;"
            cur.execute(sql_update_gui, (time_conn, False, number_id))
            self.conn.commit()
            logger.info(f"DB(gui): agent_id '{number_id}' - проверка связи успешная")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_agent_check_number_id_tru - %s : %s", number_id, e)
            raise e

    def gui_update_vvk_reg_none(self, scheme_revision: int, user_query_interval_revision: int) -> bool:
        """
            SQL-запрос на обновление статуса регистрации ВВК (NULL), то есть 'Необходима перерегистрация'.

        Args:
            scheme_revision (int): Ревизия схемы.
            user_query_interval_revision (int): Ревизия интервала пользовательских запросов.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_update_gui = ("UPDATE gui SET scheme_revision = %s, user_query_interval_revision = %s, status_reg = NULL, time_reg = NULL, error_reg = NULL "
                              "WHERE type_id = FALSE;")
            cur.execute(sql_update_gui,
                        (scheme_revision, user_query_interval_revision))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_vvk_reg_none: %s", e)
            raise e

    def gui_update_value(self, agent_id: int, error_value: str, type_id: bool) -> bool:
        """
            SQL-запрос на обновление статуса приема ПФ.

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

    def gui_update_value_out(self, vvk_id: int, agent_id: int, error_value: str) -> bool:
        """
            SQL-запрос на обновление статуса отправки ПФ.

        Args:
            vvk_id (int): Идентификатор VVK.
            agent_id (int): Идентификатор агента.
            error_value (str): Значение ошибки, если она есть.

        Returns:
            bool: Возвращает True, если обновление успешно выполнено.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            time_reg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            type_id = True
            number_id = agent_id
            if agent_id == 0:
                type_id = False
                number_id = vvk_id
            sql_update_gui = "UPDATE gui SET time_value_out = %s, error_value_out = %s WHERE number_id = %s AND type_id = %s;"
            cur.execute(sql_update_gui, (time_reg, error_value, number_id, type_id))
            self.conn.commit()
            if error_value:
                if type_id:
                    logger.error(f"DB(gui): ошибка отправки ПФ agent_id '{agent_id}': {error_value}")
                else:
                    logger.error(f"DB(gui): ошибка отправки ПФ vvk_id '{agent_id}': {error_value}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_update_value_out - vvk_id/agent_id %s/%s: %s", vvk_id, agent_id, e)
            raise e

    # __ Delete __
    def gui_delete_agents(self) -> bool:
        """
            SQL-запрос удаления из таблицы 'gui' всех агентов.

        Returns:
            bool: Возвращает True, если операция прошла успешно, иначе выбрасывается исключение.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_delete = "DELETE FROM gui WHERE type_id = TRUE; "
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info("DB(gui): таблица очищена для строк с type_id = TRUE")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(gui): gui_delete_agents: %s", e)
            raise e
