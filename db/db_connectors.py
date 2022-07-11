"""
All logic for database
"""

import datetime as date
import logging
from contextlib import closing
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2 import Error
from psycopg2._psycopg import connection
from psycopg2.extensions import cursor as PgCursor
from pydantic import BaseModel

from db.tables import CREATE_SCRIPTS

LOG = logging.getLogger(__name__)


class DBAdapter:  # responsible for Users and Chats
    def __init__(self, user, password, host, port, database, class_user_id):
        try:
            self.connection: "connection" = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database
            )
            self.cursor = self.connection.cursor()
            LOG.debug(f"[{type(self).__name__}] Соединение с базой установлено {database=}, {host=}, {port=}")
        except(Exception, Error) as ex:
            LOG.error(f"Ошибка работы с базой  {database=}, {host=}, {port=}: %s", ex)
            raise ex
        else:
            self.create_tables(conn=self.connection)
        self.class_user_id = class_user_id

    @classmethod
    def create_tables(cls, conn: "connection"):
        for script in CREATE_SCRIPTS:
            with closing(conn.cursor()) as cursor:
                cursor: "PgCursor" = cursor
                cursor.execute(script)
                conn.commit()

    def execute(self, query):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query)
            self.connection.commit()

    def rollback(self):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute("rollback")
            self.connection.commit()

    def end_transaction(self):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute('END TRANSACTION;')
            self.connection.commit()

    def fetch_one(self, query):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query)
            self.connection.commit()
            return cursor.fetchone()

    def fetchall(self, query):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def close(self):
        self.connection.close()

    def create_user(self,
                    first_name: str,
                    user_id: int,
                    nick_name=None,
                    last_name=None,
                    phone_number=None,
                    email=None):

        try:
            create_user_query = f"""
            INSERT INTO users ("UserName", "UserLastName", "UserNickName","Email", "PhoneNumber", user_id)
            VALUES ('{first_name}',' {last_name}','{nick_name}','{email}', '{phone_number}','{user_id}')
            """
            self.execute(create_user_query)
            LOG.debug(f"Пользователь {user_id} добавлен в базу")
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка работы с базой:", e)

    def update_phone_number(self, phone_number, user_id):
        try:
            update_query = f"""
                UPDATE users SET "PhoneNumber" = '{phone_number}'
                WHERE user_id = {user_id};
                """
            self.execute(update_query)
            LOG.debug(f"Телефон пользователя изменен на {phone_number}")
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при обновление телефонного номера:", e)

    def get_telegramm_name(self, user_id):
        try:
            query = f"""
                SELECT	
                    telegram_name 
                FROM public.users
                WHERE user_id = {user_id};
                        """
            result = self.fetch_one(query)
            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.debug(f"Выдача имени телеграмм", e)

    def update_telegram_name(self, telegram_name, user_id):
        try:
            update_query = f"""
                UPDATE users SET "telegram_name" = '{telegram_name}'
                WHERE user_id = {user_id};
                """
            self.execute(update_query)
            LOG.debug(f"Имя пользователя в ТГ изменено на {telegram_name}")
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при обновление имени в телеграм:", e)

    def update_telegram_link(self, tg_link, user_id):
        try:
            update_query = f"""
                UPDATE users SET "Link" = '{tg_link}'
                WHERE user_id = {user_id};
                """
            self.execute(update_query)
            LOG.debug(f"Ссылка на пользователя {tg_link}")
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при сохранения ссылки пользователя:", e)
            self.end_transaction()

    def change_nick(self):
        pass

    def get_user(self, user_id):
        if user_id is not None:
            try:
                select_query = f"""
                SELECT * 
                FROM users
                WHERE user_id={user_id} 
                """

                result = self.fetch_one(select_query)
                LOG.debug(f"Пользователь получен {user_id}: {result}")
                return result
            except(Exception, Error) as e:
                self.end_transaction()
                LOG.error("Ошибка при получение данных пользователя:", e)
        else:
            try:
                select_query = f"""
                SELECT * 
                FROM users
                WHERE user_id={self.class_user_id} 
                """
                result = self.fetch_one(select_query)
                LOG.debug(f"Пользователь получен {user_id}: {result}")
                return result
            except(Exception, Error) as e:
                self.end_transaction()
                LOG.error("Ошибка при получение данных пользователя (переменная инициализатора класса):", e)

    def get_user_tg_link(self, user_id):
        try:
            select_query = f"""
            SELECT 
            "Link"
            FROM users
            WHERE user_id={user_id} 
            """
            result = self.fetch_one(select_query)[0]
            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при получение данных ссылки тг:", e)

    def update_user_name(self, name, user_id):
        try:
            update_query = f"""
                UPDATE users SET "UserName" = '{name}'
                WHERE user_id = {user_id};
                """
            self.execute(update_query)
            LOG.debug(f"Имя пользователя изменено на {name}")
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при обновлении имени:", e)

    def create_chat(self, chat_id, user_id):
        try:
            create_chat_query = f"""
            INSERT INTO user_chat (chat_id, user_id)
            VALUES ({chat_id},{user_id});
            """
            self.execute(create_chat_query)
            LOG.debug(f"новый чат № {chat_id}  для пользователя {user_id} создан")
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при создании нового чата:", e)

    def get_offers(self) -> list:
        try:
            update_chat_query = f"""
                    SELECT 
                            u."UserName",
	                        p.title,
                            p.description,
                            p.departure_country,
                            p.departure_city,
                            p.destination_country,
                            p.destination_city,
                            p.price

                    FROM packages as p
                    LEFT JOIN public.users as u on u.user_id = p.custumer_user_id ;
            """
            result = self.fetchall(update_chat_query)
            data_list = []
            for row in result:
                data = dict()
                data['user_name'] = row[0]
                data['title'] = row[1]
                data['description'] = row[2]
                data['departure_country'] = row[3]
                data['departure_city'] = row[4]
                data['destination_country'] = row[5]
                data['destination_city'] = row[6]
                data['price'] = float(row[7])
                data_list.append(data)
            LOG.debug(f"Данные по заказам получены ")
            return data_list
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при получении данных о заказах :", e)

    def update_chat_status(self, new_status, user_id, chat_id):
        try:

            update_chat_query = f"""
            UPDATE user_chat SET "ChatStatus" = {new_status}
            WHERE chat_id = {chat_id} AND user_id = {user_id};
            """
            self.execute(update_chat_query)
            LOG.debug(f"Статус чата: {chat_id} для пользователя: {user_id} обновлен. Статус чата: {new_status}")
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при обновлении статуса :", e)

    def get_chat(self, chat_id: int) -> dict:
        try:
            select_query = f"""
            SELECT * 
            FROM user_chat
            WHERE chat_id = {chat_id} 
            """
            result = self.fetch_one(select_query)
            LOG.debug(f"Найден чат {chat_id}: {result}")
            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при получении данных о чате:", e)

    def get_chat_status(self, chat_id):
        try:
            select_query = f"""
            SELECT "ChatStatus"
            FROM user_chat
            WHERE chat_id = {chat_id} 
            """
            result = self.fetch_one(select_query)[0]
            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error(f"Ошибка при получении статуса чата {chat_id=}:", e)

    def insert_one(self, table, column1, column2, value1, value2):
        try:
            create_chat_query = f"""
             INSERT INTO {table} ({column1},{column2})
             VALUES ({value1},{value2});
             """
            self.execute(create_chat_query)
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при создании нового чата:", e)

    def ubdate_test_data(self, table, column, value, where_column, condition):
        try:
            update_chat_query = f"""
                        UPDATE {table} SET {column} = {value}
                        WHERE {where_column} = {condition};
                        """

            self.execute(update_chat_query)
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при создании нового чата:", e)

    def get_filter(self, user_id):
        try:
            select_query = f"""
            SELECT 
            *
            FROM offers_filtr
            WHERE user_id = {user_id} 
            """

            result = self.fetch_one(select_query)
            data_list = []
            data = dict()
            data['departure_country'] = result[1]
            data['departure_city'] = result[2]
            data['destination_country'] = result[3]
            data['destination_city'] = result[4]
            data['price'] = result[5]
            data_list.append(data)
            print()
            return data_list[0]
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при получении фильтра:", e)

    def update_filter(self, column, value, user_id):
        try:
            select_query = f"""
            SELECT user_id
            FROM offers_filtr
            WHERE user_id = {user_id};
            """
            result = self.fetch_one(select_query)
            if result is None:
                set_user_id_query = f"""
                INSERT INTO offers_filtr (user_id)
                VALUES ({user_id});
                """
                self.execute(set_user_id_query)
            else:
                pass
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.error("Ошибка при создании пользователя в фильтре:", e)
        finally:
            try:
                query = f"""
                            UPDATE offers_filtr SET {column} = '{value}'
                            WHERE user_id = {user_id};
                            """

                self.execute(query)
            except(Exception, Error) as e:
                self.end_transaction()
                LOG.error("Ошибка при установки фильтра:", e)

    def get_my_offers(self, user_id):
        try:
            select_query = f"""                
                    SELECT 
                        p.package_id,
                        u."UserName",
                        p.title,
                        p.description,
                        p.departure_country,
                        p.departure_city,
                        p.destination_country,
                        p.destination_city,
                        p.price,
                        o.unique_order_numner
                    FROM packages as p

            JOIN public.orders as o on o.package_id = p.package_id 
			JOIN public.users as u on u.user_id = o.executor_id 
            WHERE executor_id = {user_id} and o.status = 'in progress'
                   """

            my_offers = self.fetchall(select_query)
            return my_offers

        except(Exception, Error) as e:
            self.end_transaction()
            LOG.debug('Ошибка получения всех оферов в работе', e)

    def get_finished_offers(self, executor_id):
        try:
            query = f"""
            SELECT 
                            p.package_id,
                            o.order_start_date,
                            o.order_finish_date,
                            u."UserName",
                            p.title,
                            p.description,
                            p.departure_country,
                            p.departure_city,
                            p.destination_country,
                            p.destination_city,
                            p.price
                        FROM packages as p

                JOIN public.orders as o on o.package_id = p.package_id 
                JOIN public.users as u on u.user_id = o.costumer_id
                WHERE executor_id = {executor_id} and o.status = 'done'
"""
            result = self.fetchall(query)
            print(result)
            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.debug('Ошибка в выдаче завершенных закзаов', e)

    def query_to_dict_orders(self, rows):
        try:

            data_list = []
            data = dict()
            data['package_id'] = rows[0]
            data['user_name'] = rows[1]
            data['title'] = rows[2]
            data['description'] = rows[3]
            data['departure_country'] = rows[4]
            data['departure_city'] = rows[5]
            data['destination_country'] = rows[6]
            data['destination_city'] = rows[7]
            data['price'] = rows[8]
            data['unique_order_numner'] = rows[9]
            data_list.append(data)
            data = data_list[0]
            return data

        except(Exception, Error) as e:
            self.end_transaction()
            print('Ошибка в конвертирование даных заказов ', e)

    def query_to_dict_finishd_orders(self, rows):
        try:
            data_list = []
            data = dict()
            data['package_id'] = rows[0]
            data['order_start_date'] = rows[1]
            data['order_finish_date'] = rows[2]
            data['user_name'] = rows[3]
            data['title'] = rows[4]
            data['description'] = rows[5]
            data['departure_country'] = rows[6]
            data['departure_city'] = rows[7]
            data['destination_country'] = rows[8]
            data['destination_city'] = rows[9]
            data['price'] = rows[10]

            data_list.append(data)
            data = data_list[0]
            return data

        except(Exception, Error) as e:
            self.end_transaction()
            print('Ошибка в конвертирование даных заказов ', e)

    def get_traveler_amaunt(self):
        try:
            query = f"""
                    select count(*) from offers_filtr 
        """
            result = self.fetch_one(query)[0]

            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.debug('Ошибка в выдаче количесвта путишественников', e)

    def get_previous_chat_status(self, user_id):
        try:
            query = f"""
                    SELECT
                        previous_status
                    FROM  user_chat 
                    WHERE user_id = {user_id}
        """
            result = self.fetch_one(query)[0]

            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.debug('Ошибка в выдаче предыдущего чат статуса', e)


class GiveOffer(DBAdapter):
    def __init__(self, user, password, host, port, database, class_user_id, callback_data=None):
        super().__init__(user, password, host, port, database,class_user_id)
        self.callback_data = callback_data

    def create_package(self, custumer_user_id):
        try:
            created_date = date.date.today()
            query = f"""
            INSERT INTO packages (custumer_user_id, created_date, status)
                    VALUES ({custumer_user_id}, '{created_date}','created')
            RETURNING package_id

    """
            package_id = self.fetch_one(query)
            p_id = package_id[0]
            self.callback_data = p_id
        except(Exception, Error) as e:
            LOG.debug("Ошибка в создании посылки ", e)
            self.end_transaction()

    def write_departure_city(self, departure_city, id):
        try:
            query = f"""
            UPDATE packages SET departure_city = '{departure_city}'
            WHERE package_id = {self.callback_data} AND 
            custumer_user_id = {id}
            """
            self.execute(query)
        except(Exception, Error) as e:
            LOG.debug('Ошибка записи города отправки посылки', e)

    def write_destination_city(self, destination_city, custumer_user_id):
        try:

            query = f"""
                    UPDATE packages SET destination_city = '{destination_city}'
                    WHERE package_id = {self.callback_data} AND 
                    custumer_user_id = {custumer_user_id}
                    """
            self.execute(query)
        except(Exception, Error) as e:
            LOG.debug("Ошабка записи данных города назначения ", e)

    def write_destination_country(self, destination_country, custumer_user_id):
        try:
            query = f"""
                            UPDATE packages SET destination_country = '{destination_country}'
                            WHERE package_id = {self.callback_data} AND 
                            custumer_user_id = {custumer_user_id}
                            """
            self.execute(query)
        except(Exception, Error) as e:
            LOG.debug('ошибка записи страны назначения', e)

    def write_departure_country(self, departure_country, custumer_user_id):
        try:
            query = f"""
                        UPDATE packages SET departure_country = '{departure_country}'
                        WHERE package_id = {self.callback_data} AND 
                        custumer_user_id = {custumer_user_id}
                        """
            self.execute(query)
        except(Exception, Error) as e:
            LOG.debug('Ошибка в записи страны отправления', e)

    def write_dispatch_date(self, custumer_user_id, data):
        try:
            query = f"""
                    UPDATE packages SET despatch_date = '{data}'
                    WHERE package_id = {self.callback_data} AND 
                    custumer_user_id = {custumer_user_id}"""
            self.execute(query)
        except(Exception, Error) as e:
            LOG.debug('Ошибка в сохранении даты отправки посылки', e)

    def write_title(self, title: str, custumer_user_id):
        try:
            query = f"""
                            UPDATE packages SET title = '{title}'
                            WHERE package_id = {self.callback_data} AND 
                            custumer_user_id = {custumer_user_id}
                            """
            self.execute(query)

        except(Exception, Error) as e:
            LOG.debug('Ошибка запииса тайтла в базу ', e)

    def write_type_of_package(self, p_type: str, custumer_user_id):
        query = f"""
                UPDATE packages SET type = '{p_type}'
                WHERE package_id = {self.callback_data} AND 
                custumer_user_id = {custumer_user_id}
                """
        self.execute(query)

    def write_size_of_package(self, package_size: str, custumer_user_id):
        query = f"""
                        UPDATE packages SET package_size = '{package_size}'
                        WHERE package_id = {self.callback_data} AND 
                        custumer_user_id = {custumer_user_id}
                        """
        self.execute(query)

    def write_description(self, description, custumer_user_id):
        try:
            query = f"""
                UPDATE packages SET description = '{description}'
                WHERE package_id = {self.callback_data} AND 
                custumer_user_id = {custumer_user_id}
                """
            self.execute(query)
        except(Exception, Error) as e:

            LOG.debug('Ошибка записи описания в базу посылок', e)
        finally:
            self.rollback()

    def write_price(self, price, custumer_user_id):
        try:

            query = f"""
                        UPDATE packages SET price = {price}
                        WHERE package_id = {self.callback_data} AND 
                        custumer_user_id = {custumer_user_id}
                        """
            self.execute(query)

        except(Exception, Error) as e:
            LOG.debug('Ошибка в записи цены', e)

    def show_writen_data_to_user(self):
        query = f"""
        SELECT 
                        p.package_id,
                        u."UserName",
                        p.title,
                        p.description,
                        p.departure_country,
                        p.departure_city,
                        p.destination_country,
                        p.destination_city,
                        p.price,
                        p.despatch_date

                    FROM packages as p
                    LEFT JOIN users as u on u.user_id = p.custumer_user_id
                    WHERE package_id = {self.callback_data} AND 
                    status = 'created'

"""
        rows = self.fetch_one(query)

        data_list = []
        data = dict()
        data['package_id'] = rows[0]
        data['user_name'] = rows[1]
        data['title'] = rows[2]
        data['description'] = rows[3]
        data['departure_country'] = rows[4]
        data['departure_city'] = rows[5]
        data['destination_country'] = rows[6]
        data['destination_city'] = rows[7]
        data['price'] = rows[8]
        data['despatch_date'] = rows[9]

        data_list.append(data)
        data = data_list[0]

        text = f"""                              
<b>Информация которую ты заполнил:</b>

Что что отправляем:<i> {data['title']}</i>        
Кто заказчик:<i> {data['user_name']}</i>           
Откуда забрать                         
    Страна: <i>{data['departure_country']} </i> 
    Город: <i> {data['departure_city']}</i>     
Куда привезти                           
    Страна:<i> {data['destination_country']}</i>
    Город: <i> {data['destination_city']} </i>  
Сколько готов заплатить:<i> {data['price']}$</i>       
Описание: <i>{data['description']} </i>         
Когда когда нужно забрать <i> {data['despatch_date']}</i>
            """
        return text

    def update_package_data(self, table, column, value, where_column, condition):
        try:
            update_chat_query = f"""
                        UPDATE {table} SET {column} = {value}
                        WHERE {where_column} = {condition} AND 
                        package_id = {self.callback_data}
                        ;
                        """
            self.execute(update_chat_query)
        except(Exception, Error) as e:
            LOG.error(f"Ошибка при обновлении данных в таблице {table=} колонка {column=} данные {value=}:", e)


class OfferFilter(BaseModel):
    departure_city: str
    departure_country: Optional[str] = None
    destination_city: str
    destination_country: Optional[str] = None


class ShowOffers(DBAdapter):

    def count_rows(self, filters: OfferFilter):
        count = f"""
                SELECT 
                        COUNT(*)
                FROM packages as p
                LEFT JOIN public.users as u on u.user_id = p.custumer_user_id
                WHERE status = 'created' and  departure_city ='{filters.departure_city}'
                and  destination_country = '{filters.destination_country}';"""
        result = self.fetchall(count)
        return result[0][0]

    def get_one_row(self, filters: OfferFilter):
        query = f"""
                    SELECT 
                        p.package_id,
                        u."UserName",
                        p.title,
                        p.description,
                        p.departure_city,
                        p.destination_city,
                        p.price

                    FROM packages as p
                    LEFT JOIN users as u on u.user_id = p.custumer_user_id
                    WHERE status = 'created' and departure_city ='{filters.departure_city}'
                    and  destination_city = '{filters.destination_city}' 
                    ORDER BY package_id
                    LIMIT 1 
    """
        result = self.fetch_one(query)
        return result

    def get_next_row(self, package_id: str, filters: OfferFilter):
        query = f"""
                    SELECT 
                        p.package_id,
                        u."UserName",
                        p.title,
                        p.description,
                        p.departure_country,
                        p.departure_city,
                        p.destination_country,
                        p.destination_city,
                        p.price

                    FROM packages as p
                    LEFT JOIN public.users as u on u.user_id = p.custumer_user_id
                    WHERE status = 'created' AND 
                    departure_city ='{filters.departure_city}' AND 
                    destination_city = '{filters.destination_city}' AND 
                    package_id > {package_id}
                    
                    ORDER BY package_id
                    LIMIT 1 
"""
        result = self.fetch_one(query)
        return result

    def query_to_dict(self, rows):
        try:
            data_list = []
            data = dict()
            data['package_id'] = rows[0]
            data['user_name'] = rows[1]
            data['title'] = rows[2]
            data['description'] = rows[3]
            data['departure_city'] = rows[4]
            data['destination_city'] = rows[5]
            data['price'] = rows[6]
            data_list.append(data)
            data = data_list[0]
            return data
        except(Exception, Error) as e:
            self.end_transaction
            print('Ошибка в конвертирование даных', e)

    def previous_shown_offer(self, user_id, packeg_id: int):
        try:
            select_query = f"""
            SELECT * FROM shown_offers
            WHERE user_id = {user_id}
    """
            result = self.fetch_one(select_query)

            if result is None:
                insert_query = f"""
                INSERT INTO shown_offers (user_id, package_id)
                VALUES ({user_id}, {packeg_id})
    """
                self.execute(insert_query)

            else:
                query = f"""
                UPDATE shown_offers SET package_id = '{packeg_id}'
                WHERE user_id = {user_id};
                """
                self.execute(query)
        except(Exception, Error) as e:
            self.end_transaction()
            print('Ошибка извлечения id посылки и юзера ', e)

    def get_previous_row_id(self, user_id):
        try:
            query = f"""
                SELECT package_id 
                FROM shown_offers
                WHERE user_id = {user_id}
            """
            try:
                result = self.fetch_one(query)[0]
            except TypeError:
                query = f"""
                                SELECT package_id 
                                FROM shown_offers
                                WHERE user_id = {self.class_user_id}
                            """
                result = self.fetch_one(query)[0]
                LOG.debug(f'получен такой результат:{result}')
                return result

            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.debug('Ошибка получения ID предыдущей показанной строки', e)

    def get_user_id_by_package(self, package_id):
        try:
            query = f"""
                SELECT 
                    custumer_user_id
                FROM packages
                WHERE package_id = {package_id}
    """
            result = self.fetch_one(query)[0]
            return result
        except(Exception, Error) as e:
            self.end_transaction()
            LOG.debug('Ошибка извлечения ID пользователя по ID посылки')


class OfferWorkFilter(BaseModel):
    costumer_id: int
    executer_id: int
    package_id: int
    order_chat_id: int


class OffersInWork(DBAdapter):

    def check_working(self, filters: OfferWorkFilter):
        query = f"""
               SELECT 
               costumer_id,
               executor_id, 
               package_id
               FROM orders
               WHERE costumer_id ={filters.costumer_id} and 
               executor_id = {filters.executer_id} and package_id = {filters.package_id}
                ;
               """
        result = self.fetch_one(query)
        return result

    def check_unique_id(self, filters: OfferWorkFilter):
        query = f"""
                       SELECT 
                       unique_order_numner
                       FROM orders
                       WHERE costumer_id = {filters.costumer_id} and 
                       executor_id = {filters.executer_id} and package_id = {filters.package_id}
                        ;
                       """
        result = self.cursor.fetch_one(query)
        return result

    def star_work(self, filters: OfferWorkFilter):

        gen_unique_number = f"{filters.package_id}{datetime.now().time().minute}{datetime.now().time().second}"
        order_start_date = datetime.now()
        query_orders = f"""
        INSERT INTO orders ( costumer_id, executor_id, order_start_date, package_id, order_chat_id, status, unique_order_numner)
        VALUES ('{filters.costumer_id}', '{filters.executer_id}','{order_start_date}','{filters.package_id}', 
        '{filters.order_chat_id}', 'in progress', '{gen_unique_number}');
        """
        self.execute(query_orders)

        query_packages = f"""
                UPDATE packages 
                SET status = 'in progress'
                WHERE package_id = {filters.package_id};
                """
        self.execute(query_packages)

    def end_work(self, unique_order_number, filters: OfferWorkFilter):
        try:
            order_stop_date = datetime.now()
            query = f"""
            UPDATE orders 
            SET order_finish_date = '{order_stop_date}', status = 'done'
            WHERE unique_order_numner = {unique_order_number} ;
            """
            self.execute(query)

            query_packages = f"""
                            UPDATE packages 
                            SET status = 'done'
                            WHERE package_id = {filters.package_id};
                            """
            self.execute(query_packages)
        except(Exception, Error) as e:
            LOG.debug('Ошибка окончания заказа', e)

# class DBOffersManager:
#
#     @classmethod
#     def create_database(cls, user, password, host, port, database):
#         engine = create_engine(url=f"postgresql://{user}:{password}@{host}:{port}")
#         with Session(engine) as session:
#             session.execute(f"create database '{database}' if not exists;")
#
#     def __init__(self, user, password, host, port, database):
# #        self.create_database(user, password, host, port, database)
#         self.engine = create_engine(url=f"postgresql://{user}:{password}@{host}:{port}/{database.lower()}")
#         SQLModel.metadata.create_all(self.engine)
#
#     def close(self):
#         pass
#
#     def add_offer(self, offer: OfferInDB):
#         with Session(self.engine) as session:
#             session.add(offer)
#             session.commit()
#             session.refresh(offer)
#             return offer
#
#     def find_one_offer(self, filters: OfferFilter) -> OfferInDB:
#         params = [
#             OfferInDB.departure_city == filters.departure_city,
#             OfferInDB.destination_country == filters.destination_country
#         ]
#         if filters.departure_country is not None:
#             params.append(OfferInDB.departure_country == filters.departure_country)
#
#         with Session(self.engine) as session:
#             statement = select(OfferInDB).where(and_(*params))
#             offer: "OfferInDB" = session.exec(statement).first()
#             return offer
