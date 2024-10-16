import json

from logger.logger import logger
from myException import MyException427

class Reg_sch:

    # ____________ REG_SCH _____________

    # __ Select __
    # __ VVK __
    def reg_sch_select_vvk_all(self) -> tuple:
        """
            SQL-запрос на получение всей информации о ВВК.

        Возвращает:
            tuple: Кортеж, содержащий значения полей 'scheme_revision', 'user_query_interval_revision',
                   'original_scheme', 'scheme', 'max_index,' и 'metric_info_list'.

        Raises:
            MyException427: Если не загружена join scheme
            Exception: Если не найдено ни одной записи или произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = """
                SELECT scheme_revision, user_query_interval_revision, original_scheme, scheme, max_index, metric_info_list
                FROM reg_sch
                WHERE type_id = FALSE
            """
            cur.execute(sql_select, )
            result = cur.fetchone()
            self.conn.commit()
            if result:
                return result
            else:
                raise MyException427("(RU) JoinScheme не загружен! (ENG) JoinScheme is not loaded!")
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_vvk_all: %s", e)
            raise e

    def reg_sch_select_check_vvk(self) -> bool:
        """
            SQL-запрос на наличие схемы ВВК в таблице 'reg_sch'.

        Returns:
            bool: Возвращает True, если существуют ВВК схему, иначе False.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_check = "SELECT 1 FROM reg_sch WHERE type_id = FALSE LIMIT 1;"
            cur.execute(sql_check)
            result = cur.fetchone()
            self.conn.commit()
            return result is not None
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_check_vvk: %s", e)
            raise e

    def reg_sch_select_vvk_metric_info_list(self) -> dict:
        """
        SQL-запрос для получения 'metric_info_list' схему ВВК.

        Returns:
            dict: Словарь, содержащий ключ 'metric_info_list' и соответствующее значение.

        Raises:
            MyException427: Если запись не найдена
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT metric_info_list FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            self.conn.commit()
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                raise MyException427("(RU) JoinScheme не загружен! (ENG) JoinScheme is not loaded!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_vvk_full: %s", e)
            raise e

    def reg_sch_select_vvk_templates(self) -> list:
        """
            SQL-запрос для выбора уникальных template_id JoinScheme.

        Args:
            agent_id (int): Идентификатор агента, template_id которого исключаются.

        Returns:
            list: Список уникальных template_id, за исключением шаблонов указанного агента.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT DISTINCT jsonb_array_elements(original_scheme->'templates')->>'template_id' AS template_id
                    FROM reg_sch
                    WHERE type_id = False;
                """
            cur.execute(sql_select, )
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return []
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_vvk_templates: %s", e)
            raise e

    # __ AGENTS __
    def reg_sch_select_max_index_agents(self) -> int:
        """
            SQL-запрос: на получение максимального зарегистрированного индекса среди агентов.

        Returns:
            int: Количество зарегистрированных агентов в базе данных.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_count_agents = "SELECT number_id FROM reg_sch WHERE type_id = TRUE ORDER BY number_id DESC LIMIT 1;"
            cur.execute(sql_count_agents)
            result = cur.fetchone()

            if result is not None:
                return result[0]
            else:
                return 0
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_count_agents: %s", e)
            raise

    def reg_sch_select_agents_all_json(self) -> list:
        """
            SQL-запрос на извлечение все записи агента, а именно:
            number_id, agent_reg_id, scheme_revision, original_scheme, scheme

        Returns:
            list: Список словарей, содержащих данные из таблицы 'reg_sch'.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT number_id, agent_reg_id, scheme_revision, original_scheme, scheme, response_scheme 
                    FROM reg_sch 
                    WHERE type_id = TRUE
                """
            cur.execute(sql_select, )
            results = cur.fetchall()
            self.conn.commit()
            column_names = [desc[0] for desc in cur.description]
            result_dicts = [dict(zip(column_names, row)) for row in results]
            return result_dicts
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_agents_all: %s", e)
            raise e

    def reg_sch_select_metrics_and_items_for_agent(self, agent_id: int) -> tuple:
        """
            SQL-запрос для получения metric_id и item_id для заданного агента.

        Args:
            agent_id (int): Идентификатор агента.

        Returns:
            tuple: Кортеж, содержащий информацию о агенте.
                   Формат кортежа: (scheme_revision, user_query_interval_revision, metrics_id, items_id).
                   Если нет данных, возвращает (None, None, [], []).

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_query = (f"SELECT scheme_revision, user_query_interval_revision, "
                         f"jsonb_array_elements(scheme->'metrics')->>'metric_id' AS metric_id, "
                         f"jsonb_array_elements(scheme->'item_id_list')->>'item_id' AS item_id "
                         f"FROM reg_sch "
                         f"WHERE number_id = {agent_id} AND type_id = TRUE; ")
            cur.execute(sql_query)
            result = cur.fetchall()
            self.conn.commit()
            if result:
                scheme_revision = result[0][0]
                user_query_interval_revisions = result[0][1]
                metrics_id = [row[2] for row in result if row[2] is not None]
                items_id = [row[3] for row in result if row[3] is not None]
                return scheme_revision, user_query_interval_revisions, metrics_id, items_id
            return None, None, [], []
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_metrics_and_items: %s", e)
            raise e

    def reg_sch_select_agent_scheme(self, agent_id: int) -> tuple:
        """
            SQL-запрос на получение всей информации об агенте.

        Args:
            agent_id (int): Идентификатор агента, для которого необходимо извлечь данные.

        Returns:
            tuple: Кортеж, содержащий значения полей 'scheme_revision', 'user_query_interval_revision',
            'original_scheme', 'scheme' и 'response_scheme'.

        Raises:
            MyException427: Если агент с заданным идентификатором не найден
            Exception: Если не найдено ни одной записи или произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = ("SELECT scheme_revision, user_query_interval_revision, original_scheme, scheme, response_scheme, metric_info_list FROM reg_sch "
                          "WHERE number_id = %s AND type_id = True; ")
            cur.execute(sql_select, (agent_id,))
            data = cur.fetchone()
            self.conn.commit()
            if data:
                return data
            else:
                raise MyException427(f"(RU) Агент '{agent_id}' не зарегистрирован! (ENG) This agent '{agent_id}' is not registered!")
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_agent_scheme: %s", e)
            raise e

    def reg_sch_select_agent_details(self, agent_id: int) -> tuple:
        """
            SQL-запрос для получения 'scheme_revision' и 'user_query_interval_revision' агента.

        Args:
            agent_id (int): Идентификатор агента, для которого требуется получить 'scheme_revision' и 'user_query_interval_revision'.

        Returns:
            tuple: Кортеж, содержащий 'scheme_revision' и 'user_query_interval_revision'.

        Raises:
            MyException427: Если агент с заданным идентификатором не найден
            Exception: Если произошла ошибка при выполнении запроса.

        """
        try:
            cur = self.conn.cursor()
            sql_select = (f"SELECT scheme_revision, user_query_interval_revision FROM reg_sch "
                          f"WHERE number_id = {agent_id} AND type_id = True; ")
            cur.execute(sql_select, )
            data = cur.fetchone()
            self.conn.commit()
            if data:
                return data
            else:
                raise MyException427(f"(RU) Агент '{agent_id}' не зарегистрирован! (ENG) This agent '{agent_id}' is not registered!")
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_agent_details: %s", e)
            raise e

    def reg_sch_select_agent_details2(self, agent_id: int) -> tuple:
        """
            SQL-запрос для получения 'agent_reg_id' и 'scheme_revision' агента.

        Args:
            agent_id (int): Идентификатор агента, для которого требуется получить 'agent_reg_id' и 'scheme_revision'.

        Returns:
            tuple: Кортеж, содержащий 'agent_reg_id' и 'scheme_revision'.

        Raises:
            MyException427: Если агент с заданным идентификатором не найден
            Exception: Если произошла ошибка при выполнении запроса.

        """
        try:
            cur = self.conn.cursor()
            sql_select = (f"SELECT agent_reg_id, scheme_revision FROM reg_sch "
                          f"WHERE number_id = {agent_id} AND type_id = True; ")
            cur.execute(sql_select, )
            result = cur.fetchone()
            self.conn.commit()
            if result:
                return result
            else:
                raise MyException427(f"(RU) Агент '{agent_id}' не зарегистрирован! (ENG) This agent '{agent_id}' is not registered!")
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_agent_details2: %s", e)
            raise e

    def reg_sch_select_agent_user_q(self, agent_id: int) -> int:
        """
            SQL-запрос для получения 'user_query_interval_revision' агента.

        Args:
            agent_id (int): Идентификатор агента.

        Returns:
            int: Значение 'user_query_interval_revision' или None, если агент не найден.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = (f"SELECT user_query_interval_revision FROM reg_sch "
                          f"WHERE number_id = {agent_id} AND type_id = True; ")
            cur.execute(sql_select)
            data = cur.fetchone()
            self.conn.commit()
            if data:
                return data[0]
            else:
                return None
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_agent_user_q: %s", e)
            raise e

    def reg_sch_select_templates_excluding_agent(self, agent_id: int) -> list:
        """
            SQL-запрос для выбора уникальных template_id, исключая шаблоны указанного агента.

        Args:
            agent_id (int): Идентификатор агента, template_id которого исключаются.

        Returns:
            list: Список уникальных template_id, за исключением шаблонов указанного агента.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT DISTINCT jsonb_array_elements(original_scheme->'templates')->>'template_id' AS template_id
                    FROM reg_sch
                    WHERE number_id != %s AND type_id = True;
                """
            cur.execute(sql_select, (agent_id,))
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return []
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_templates_excluding_agent: %s", e)
            raise e

    def reg_sch_select_metrics_excluding_agent(self, agent_id: int) -> list:
        """
            SQL-запрос для выбора уникальных metric_id, исключая метрики указанного агента.

        Args:
            agent_id (int): Идентификатор агента, metric_id которого исключаются.

        Returns:
            list: Список уникальных metric_id, за исключением метрик указанного агента.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT DISTINCT jsonb_array_elements(original_scheme->'metrics')->>'metric_id' AS metric_id
                    FROM reg_sch
                    WHERE number_id != %s
                """
            cur.execute(sql_select, (agent_id,))
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return []
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_select_metrics_excluding_agent: %s", e)
            raise e

    def reg_sch_select_agent_item_id_list(self, agent_id: int) -> list:
        """
        SQL-запрос для получения 'item_id_list' агента.

        Args:
            agent_id (int): Идентификатор агента.

        Returns:
            list: Список item_id_list.
                  В случае отсутствия записей возвращает пустой список.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.

        """
        try:
            cur = self.conn.cursor()
            sql_select = """
                    SELECT jsonb_array_elements(scheme->'item_id_list') AS item_id_list
                    FROM reg_sch
                    WHERE number_id = %s AND type_id = True
                """
            cur.execute(sql_select, (agent_id,))
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return []
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_full_paths_agent: %s", e)
            raise e

    # __ Insert __
    def reg_sch_insert_vvk(self, scheme_revision: int, original_scheme: dict, scheme: dict, max_index: int, metric_info_list: dict) -> bool:
        """
            SQL-запрос для вставки информации о схеме ВВК, включая ревизию схемы,
        оригинальную схему, текущую схему и список метрик инфо.

        Args:
            scheme_revision (int): Ревизия схемы.
            original_scheme (dict): Оригинальная схема в виде словаря.
            scheme (dict): Текущая схема в виде словаря.
            max_index (int): Максимальный индекс для item_id.
            metric_info_list (dict): Список метрик инфо в виде словаря.

        Returns:
            bool: Возвращает True, если операция прошла успешно, иначе выбрасывается исключение.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_insert_scheme = (
                "INSERT INTO reg_sch (type_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, max_index, metric_info_list) "
                "VALUES (FALSE, %s, %s, %s, %s, %s, %s);")
            cur.execute(sql_insert_scheme, (scheme_revision, 0, json.dumps(original_scheme), json.dumps(scheme), max_index, json.dumps(metric_info_list)))
            self.conn.commit()
            logger.info("DB(reg_sch): VvkScheme зарегистрирована")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_insert_vvk: %s", e)
            raise e

    def reg_sch_insert_agent(self, number_id: int, agent_reg_id: str, scheme_revision: int,
                             user_query_interval_revision: int, original_scheme: dict, scheme: dict, response_scheme: dict) -> bool:
        """
            SQL-запрос: Вставляет данные нового агента в таблицу 'reg_sch'.

        Args:
            number_id (int): Идентификатор агента.
            agent_reg_id (str): Регистрационный идентификатор агента.
            scheme_revision (int): Номер ревизии схемы.
            user_query_interval_revision (int): Номер ревизии интервала пользовательского запроса.
            original_scheme (dict): Оригинальная схема агента.
            scheme (dict): Зарегистрированная схема агента.
            response_scheme (dict): Ответ для агента с его item_id.

        Returns:
            bool: Возвращает True, если данные агента успешно вставлены в базу данных.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_insert = (
                "INSERT INTO reg_sch (type_id, number_id, agent_reg_id, scheme_revision, user_query_interval_revision, original_scheme, scheme, response_scheme, metric_info_list) "
                "VALUES (TRUE, %s, %s, %s, %s, %s, %s, %s, %s);")
            cur.execute(sql_insert, (
            number_id, agent_reg_id, scheme_revision, user_query_interval_revision, json.dumps(original_scheme),
            json.dumps(scheme), json.dumps(response_scheme), None))
            self.conn.commit()
            logger.info(f"DB(reg_sch): Agent '{number_id}' зарегистрирован")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_insert_agent '%s': %s", number_id, e)
            raise e

    # __ Update __
    def reg_sch_update_vvk_scheme(self, scheme_revision: int, scheme: dict, max_index: int, metric_info_list: dict) -> bool:
        """
            SQL-запрос: Обновляет схему VVK в таблице.

        Args:
            scheme_revision (int): Номер ревизии схемы.
            scheme (dict): Схема VVK в формате словаря.
            max_index (int): Максимальный индекс для item_id.
            metric_info_list (dict): Метрики.

        Returns:
            bool: Возвращает True, если обновление схемы выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_update_scheme = ("UPDATE reg_sch SET scheme_revision = %s, scheme = %s, max_index = %s, metric_info_list = %s "
                                 "WHERE type_id = FALSE;")
            cur.execute(sql_update_scheme, (scheme_revision, json.dumps(scheme), max_index, json.dumps(metric_info_list),))
            logger.info("DB(reg_sch): VvkScheme-scheme изменена")
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_vvk_scheme: %s", e)
            raise e

    def reg_sch_update_vvk_scheme_all(self, scheme_revision: int, original_scheme: dict, scheme: dict, max_index: int,
                                      metric_info_list_raw: dict) -> bool:
        """
            SQL-запрос на обновление 'reg_sch' после перерегистрации новой Join схемы.

        Args:
            scheme_revision (int): Новая ревизия схемы.
            original_scheme (dict): Новая join схема.
            scheme (dict): Новая схема VVK.
            max_index (int): Максимальный индекс для item_id.
            metric_info_list_raw (dict): Метрики.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_update_scheme = ("UPDATE reg_sch SET scheme_revision = %s, original_scheme = %s, scheme = %s, max_index = %s, metric_info_list = %s "
                                 "WHERE type_id = FALSE;")
            cur.execute(sql_update_scheme, (scheme_revision, json.dumps(original_scheme), json.dumps(scheme), max_index, json.dumps(metric_info_list_raw),))
            logger.info("DB(reg_sch): VvkScheme-scheme изменена")
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_vvk_scheme: %s", e)
            raise e

    def reg_sch_update_agent_re_reg(self, number_id: int, scheme_revision: int, user_query_interval_revision: int,
                                    original_scheme: dict, scheme: dict, response_scheme: dict, metric_info_list: dict) -> bool:
        """
            SQL-запрос для обновления записи агента после перерегистрации.

        Args:
            number_id (int): Идентификатор агента.
            scheme_revision (int): Новая ревизия схемы
            user_query_interval_revision (int): Номер ревизии интервала пользовательского запроса.
            original_scheme (dict): Исходная схема агента.
            scheme (dict): Зарегистрированная схема агента.
            response_scheme (dict): Ответ для агента с его item_id.
            metric_info_list (dict): МИЛ, который отправил агент.

        Returns:
            bool: True, если обновление прошло успешно, иначе возбуждается исключение.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_update = (f"UPDATE reg_sch SET scheme_revision = %s, user_query_interval_revision = %s, original_scheme = %s, scheme = %s, response_scheme = %s, metric_info_list = %s "
                          f"WHERE number_id = {number_id} AND type_id = True")
            cur.execute(sql_update, (
            scheme_revision, user_query_interval_revision, json.dumps(original_scheme), json.dumps(scheme), json.dumps(response_scheme), json.dumps(metric_info_list),))
            self.conn.commit()
            logger.info(f"DB(reg_sch): Agent '{number_id}' перерегистрирована")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_agent_re_reg '%s': %s", number_id, e)
            raise e

    def reg_sch_delete_mil(self, metric_info_list: dict) -> bool:
        """
        SQL-запрос для обновления metric_info_list записи схемы ВВК.

        Args:
            metric_info_list (dict): Список информации о метриках.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_update = (
                "UPDATE reg_sch SET metric_info_list = %s "
                "WHERE type_id = False;")
            cur.execute(sql_update, (json.dumps(metric_info_list),))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(sch_ver): reg_sch_delete_mil: %s", e)
            raise e


    # __ Delete __
    def reg_sch_delete_agent(self, agent_id: int) -> bool:
        """
            SQL-запрос на удаление агента из таблицы 'reg_sch'.

        Args:
            agent_id (int): Идентификатор агента, запись которого необходимо удалить.

        Returns:
            bool: Возвращает True, если удаление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_delete = f"DELETE FROM reg_sch WHERE number_id = {agent_id} AND type_id = True;"
            cur.execute(sql_delete)
            self.conn.commit()
            logger.info(f"DB(reg_sch): удален агент {agent_id}")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_delete_agent: %s", e)
            raise e

    # __ BLOCK __
    def reg_sch_block_true(self) -> bool:
        """
            SQL-запрос, который блокирует изменение схемы ВВК.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_update = "UPDATE reg_sch SET block = TRUE WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение block успешно изменено на True")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_block_true: %s", e)
            raise e

    def reg_sch_block_false(self) -> bool:
        """
            SQL-запрос, который снимает блокировку на изменение схемы ВВК.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_update = "UPDATE reg_sch SET block = FALSE WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение block успешно изменено на False")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_block_false: %s", e)
            raise e

    def reg_sch_block_check(self) -> bool:
        """
            SQL-запрос, который проверяет возможность изменить схему ВВК.

        Returns:
            bool: Возвращает True, если обновление прошло успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса к базе данных.
        """
        try:
            cur = self.conn.cursor()
            sql_query = "SELECT block FROM reg_sch WHERE type_id = FALSE;"
            cur.execute(sql_query)
            self.conn.commit()
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            logger.error("DB(reg_sch): reg_sch_check_block: %s", e)
            raise e