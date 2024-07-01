import json

from logger.logger import logger


class Reg_sch:

# ____________ REG_SCH _____________

# __ Create Table __
    def reg_sch_create_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_create_table = """
                CREATE TABLE IF NOT EXISTS reg_sch (
                    id SERIAL PRIMARY KEY,
                    type_id BOOLEAN,
                    number_id INT,
                    agent_reg_id VARCHAR(30),
                    scheme_revision INT,
                    user_query_interval_revision INT,
                    original_scheme JSONB,
                    scheme JSONB,
                    max_index INT,
                    metric_info_list JSONB,
                    block BOOLEAN DEFAULT FALSE
                );
            """
            cur.execute(sql_create_table)
            self.conn.commit()
            logger.info("DB(reg_sch): таблица создана")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_create_table: %s", e)
            raise e

# __ Drop Table __
    def reg_sch_drop_table(self) -> bool:
        try:
            cur = self.conn.cursor()
            sql_drop_table = "DROP TABLE IF EXISTS reg_sch;"
            cur.execute(sql_drop_table)
            self.conn.commit()
            logger.info("DB(reg_sch): таблица удалена")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_drop_table: %s", e)
            raise e

# __ Select __
    # __ VVK __
    def reg_sch_select_vvk_scheme(self):
        """
            SQL-запрос: Извлекает данные схемы VVK для ее регистрации.

        Returns:
            tuple: Кортеж, содержащий scheme_revision, scheme и metric_info_list.

        Raises:
            Exception: Если данные схемы VVK не найдены или происходит ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT scheme_revision, scheme, metric_info_list FROM reg_sch WHERE type_id = FALSE"
            cur.execute(sql_select, )
            result = cur.fetchone()
            if result:
                return result
            else:
                raise Exception("VvkScheme не зарегистирована!!")
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_vvk_scheme: %s", e)
            raise e

    # __ AGENTS __
    def reg_sch_select_number_id(self) -> list:
        """
            SQL-запрос: Извлекает идентификаторы всех агентов и ввк.

        Returns:
            list: Список, содержащий number_id.

        Raises:
            Exception: Если данные схемы VVK не найдены или происходит ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_select = "SELECT number_id FROM reg_sch"
            cur.execute(sql_select)
            result = cur.fetchall()

            number_ids = [row[0] for row in result]

            return number_ids

        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_select_number_if: %s", e)
            raise e

# __ Insert __


# __ Update __
    def reg_sch_update_vvk_id(self, vvk_id: int) -> bool:
        """
            SQL-запрос: Обновляет идентификатор зарегистрированной VVK в таблице reg_sch.

        Args:
            vvk_id (int): Новый идентификатор зарегистрированной VVK.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE reg_sch SET number_id = {vvk_id} WHERE type_id = FALSE;"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info(f"DB(reg_sch): значение vvk_id '{vvk_id}' успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_vvk_id: %s", e)
            raise e

    def reg_sch_update_all_user_query_revision(self, user_query_interval_revision: int) -> bool:
        """
            SQL-запрос: Обновляет версию интервала запроса пользователя в таблице reg_sch для всех записей.

        Args:
            user_query_interval_revision (int): Новая версия интервала запроса пользователя.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_update = f"UPDATE reg_sch SET user_query_interval_revision = {user_query_interval_revision};"
            cur.execute(sql_update)
            self.conn.commit()
            logger.info("DB(reg_sch): значение user_query_interval_revision успешно изменено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_all_user_query_revision: %s", e)
            raise e

    def reg_sch_update_vvk_metric_info(self, metric_info_list: dict) -> bool:
        """
        SQL-запрос: Обновляет metric_info_list зарегистрированной VVK в таблице reg_sch.

        Args:
            metric_info_list (dict): Новый метрики VVK.

        Returns:
            bool: Возвращает True, если обновление выполнено успешно.

        Raises:
            Exception: Если произошла ошибка при выполнении запроса.
        """
        try:
            cur = self.conn.cursor()
            sql_update = """
                UPDATE reg_sch
                SET metric_info_list = %s
                WHERE type_id = FALSE;
            """
            cur.execute(sql_update, (json.dumps(metric_info_list),))
            self.conn.commit()
            logger.info("DB(reg_sch): значение metric_info_list успешно обновлено")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("DB(reg_sch): reg_sch_update_vvk_metric_info: %s", e)
            raise e


# __ Delete __

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









