"""
All logic for database
"""

import datetime as date
import logging
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2 import Error
from psycopg2._psycopg import connection
from pydantic import BaseModel
from sqlalchemy import and_
from sqlmodel import Session, SQLModel, create_engine, select

from db.tables import OfferInDB

LOG = logging.getLogger(__name__)


class DBAdapter:  # responsible for Users and Chats
    def __init__(self, user, password, host, port, database, ):
        try:
            self.connection: "connection" = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database
            )
            self.cursor = self.connection.cursor()
            LOG.debug("Соединение с базой установлено")
        except(Exception, Error) as e:
            LOG.error("Ошибка работы с базой:", e)

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
            self.cursor.execute(create_user_query)
            self.connection.commit()
            LOG.debug("Пользователь добавлен в базу")

        except(Exception, Error) as e:
            LOG.error("Ошибка работы с базой:", e)

    def update_phone_number(self, phone_number, user_id):
        try:
            update_query = f"""
                UPDATE users SET "PhoneNumber" = '{phone_number}'
                WHERE user_id = {user_id};
                """
            self.cursor.execute(update_query)
            self.connection.commit()
            LOG.debug(f"Телефон пользователя изменен на {phone_number}")
        except(Exception, Error) as e:
            LOG.error("Ошибка при обновление телефонного номера:", e)

    def change_nick(self):
        pass

    def get_user(self, user_id) -> dict:
        try:
            select_query = f"""
            SELECT * 
            FROM users
            WHERE user_id={user_id} 
            """
            self.cursor.execute(select_query)
            result = self.cursor.fetchone()
            return result
        except(Exception, Error) as e:
            LOG.error("Ошибка при получение данных пользователя:", e)

    def update_user_name(self, name, user_id):
        try:
            update_query = f"""
                UPDATE users SET "UserName" = '{name}'
                WHERE user_id = {user_id};
                """
            self.cursor.execute(update_query)
            self.connection.commit()
            LOG.debug(f"Имя пользователя изменено на {name}")
        except(Exception, Error) as e:
            LOG.error("Ошибка при обновлении имени:", e)

    def create_chat(self, chat_id, user_id):
        try:
            create_chat_query = f"""
            INSERT INTO user_chat (chat_id, user_id)
            VALUES ({chat_id},{user_id});
            """
            self.cursor.execute(create_chat_query)
            self.connection.commit()
            LOG.debug(f"новый чат № {chat_id}  для пользователя {user_id} создан")
        except(Exception, Error) as e:
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
            self.cursor.execute(update_chat_query)
            self.connection.commit()
            result = self.cursor.fetchall()
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
            LOG.error("Ошибка при получении данных о заказах :", e)

    def update_chat_status(self, new_status, user_id, chat_id):
        try:
            update_chat_query = f"""
            UPDATE user_chat SET "ChatStatus" = {new_status}
            WHERE chat_id = {chat_id} AND user_id = {user_id};
            """
            self.cursor.execute(update_chat_query)
            self.connection.commit()
            LOG.debug(f"Статус чата: {chat_id} для пользователя: {user_id} обновлен. Статус чата: {new_status}")
        except(Exception, Error) as e:
            LOG.error("Ошибка при обновлении статуса :", e)

    def get_chat(self, chat_id) -> dict:
        try:
            select_query = f"""
            SELECT * 
            FROM user_chat
            WHERE chat_id = {chat_id} 
            """
            self.cursor.execute(select_query)
            result = self.cursor.fetchone()
            return result
        except(Exception, Error) as e:
            LOG.error("Ошибка при получении данных о чате:", e)

    def get_chat_status(self, chat_id):
        try:
            select_query = f"""
            SELECT 
            "ChatStatus"
            FROM user_chat
            WHERE chat_id = {chat_id} 
            """
            self.cursor.execute(select_query)
            result = self.cursor.fetchone()[0]
            return result
        except(Exception, Error) as e:
            LOG.error("Ошибка при получении статуса чата:", e)

    def insert_one(self, table, column1, column2, value1, value2):
        try:
            create_chat_query = f"""
             INSERT INTO {table} ({column1},{column2})
             VALUES ({value1},{value2});
             """
            self.cursor.execute(create_chat_query)
            self.connection.commit()
        except(Exception, Error) as e:
            LOG.error("Ошибка при создании нового чата:", e)

    def ubdate_test_data(self, table, column, value, where_column, condition):
        try:
            update_chat_query = f"""
                        UPDATE {table} SET {column} = {value}
                        WHERE {where_column} = {condition};
                        """

            self.cursor.execute(update_chat_query)
            self.connection.commit()
        except(Exception, Error) as e:
            LOG.error("Ошибка при создании нового чата:", e)

    def get_filter(self, user_id):
        try:
            select_query = f"""
            SELECT 
            *
            FROM offers_filtr
            WHERE user_id = {user_id} 
            """
            self.cursor.execute(select_query)
            result = self.cursor.fetchone()
            data_list = []
            data = dict()
            data['departure_country'] = result[1]
            data['departure_city'] = result[2]
            data['destination_country'] = result[3]
            data['destination_city'] = result[4]
            data['price'] = result[5]
            data_list.append(data)
            return data_list[0]
        except(Exception, Error) as e:
            LOG.error("Ошибка при получении фильтра:", e)

    def update_filter(self, column, value, user_id):
        try:
            select_query = f"""
            SELECT user_id
            FROM offers_filtr
            WHERE user_id = {user_id};
            """
            self.cursor.execute(select_query)
            result = self.cursor.fetchone()
            if result == None:
                set_user_id_query = f"""
                INSERT INTO offers_filtr (user_id)
                VALUES ({user_id});
                """
                self.cursor.execute(set_user_id_query)
                self.connection.commit()
            else:
                pass
        except(Exception, Error) as e:
            LOG.error("Ошибка при создании пользователя в фильтре:", e)
        finally:
            try:
                query = f"""
                            UPDATE offers_filtr SET {column} = '{value}'
                            WHERE user_id = {user_id};
                            """

                self.cursor.execute(query)
                self.connection.commit()
            except(Exception, Error) as e:
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

            self.cursor.execute(select_query)
            self.connection.commit()
            my_offers = self.cursor.fetchall()
            return my_offers

        except(Exception, Error) as e:
            LOG.debug('Ошибка получения всех оферов в работе', e)

    def get_finished_offers(self):
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
                JOIN public.users as u on u.user_id = o.executor_id 
                WHERE executor_id = 301213126 and o.status = 'done'
"""
            self.cursor.execute(query)
            self.connection.commit()
            result = self.cursor.fetchall()
            print(result)
            return result
        except(Exception, Error) as e:
            LOG.debug('Ошибка в выдаче завершенных закзаов', e)

    @staticmethod
    def query_to_dict_orders(rows):
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
            print('Ошибка в конвертирование даных заказов ', e)

    @staticmethod
    def query_to_dict_finishd_orders(rows):
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
            print('Ошибка в конвертирование даных заказов ', e)


class GiveOffer(DBAdapter):
    def __init__(self, user, password, host, port, database, callback_data=None):
        super().__init__(user, password, host, port, database)
        self.callback_data = callback_data

    def create_package(self, custumer_user_id):
        try:
            created_date = date.date.today()
            query = f"""
            INSERT INTO packages (custumer_user_id, created_date,status)
                    VALUES ({custumer_user_id}, '{created_date}','created')
            RETURNING package_id

    """
            self.cursor.execute(query)
            self.connection.commit()
            package_id = self.cursor.fetchone()[0]
            self.callback_data = package_id
        except(Exception, Error) as e:
            LOG.debug("Ошибка в создании посылки ", e)

    def write_departure_city(self):
        print(self.callback_data)

    def write_destination_city(self):
        print(self.callback_data)

    def write_dispatch_date(self):
        pass

    def write_type_of_package(self):
        pass

    def write_size_of_package(self):
        pass

    def write_description(self):
        pass

    def write_price(self):
        pass


class OfferFilter(BaseModel):
    departure_city: str
    destination_country: str
    departure_country: Optional[str] = None


class ShowOffers(DBAdapter):
    def __init__(self, user, password, host, port, database):
        super().__init__(user, password, host, port, database)

    def count_rows(self, filters: OfferFilter):
        count = f"""
                SELECT 
                        COUNT(*)
                FROM packages as p
                LEFT JOIN public.users as u on u.user_id = p.custumer_user_id
                WHERE status = 'created' and  departure_city ='{filters.departure_city}'
                and  destination_country = '{filters.destination_country}';"""
        self.cursor.execute(count)
        self.connection.commit()
        result = self.cursor.fetchall()
        return result[0][0]

    def get_one_row(self, filters: OfferFilter):
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
                    WHERE status = 'created' and departure_city ='{filters.departure_city}'
                    and  destination_country = '{filters.destination_country}' 
                    ORDER BY package_id
                    LIMIT 1 
    """
        self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
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
                    destination_country = '{filters.destination_country}' AND 
                    package_id > {package_id}
                    
                    ORDER BY package_id
                    LIMIT 1 
"""
        self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
        return result

    @staticmethod
    def query_to_dict(rows):
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
            data_list.append(data)

            data = data_list[0]
            return data
        except(Exception, Error) as e:
            print('Ошибка в конвертирование даных', e)

    def previous_shown_offer(self, user_id, packeg_id: int):
        try:
            select_query = f"""
            SELECT * FROM shown_offers
            WHERE user_id = {user_id}
    """
            self.cursor.execute(select_query)
            self.connection.commit()
            result = self.cursor.fetchone()

            if result is None:
                insert_query = f"""
                INSERT INTO shown_offers (user_id, package_id)
                VALUES ({user_id}, {packeg_id})
    """
                self.cursor.execute(insert_query)
                self.connection.commit()

            else:
                query = f"""
                UPDATE shown_offers SET package_id = '{packeg_id}'
                WHERE user_id = {user_id};
                """
                self.cursor.execute(query)
                self.connection.commit()
        except(Exception, Error) as e:
            print('Ошибка извлечения id посылки и юзера ', e)

    def get_previous_row_id(self, user_id):
        try:
            query = f"""
                SELECT package_id 
                FROM public.shown_offers
                WHERE user_id = {user_id}
            """
            self.cursor.execute(query)
            self.connection.commit()
            result = self.cursor.fetchone()[0]
            return result
        except(Exception, Error) as e:
            LOG.debug('Ошибка получения ID предыдущей показанной строки', e)

    def get_user_id_by_package(self, package_id):
        try:
            query = f"""
                SELECT 
                    custumer_user_id
                FROM packages
                WHERE package_id = {package_id}
    """
            self.cursor.execute(query)
            self.connection.commit()
            result = self.cursor.fetchone()[0]
            return result
        except(Exception, Error) as e:
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
        self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
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
        self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
        return result

    def star_work(self, filters: OfferWorkFilter):

        gen_unique_number = f"{filters.package_id}{datetime.now().time().minute}{datetime.now().time().second}"
        order_start_date = datetime.now()
        query_orders = f"""
        INSERT INTO orders ( costumer_id, executor_id, order_start_date, package_id, order_chat_id, status, unique_order_numner)
        VALUES ('{filters.costumer_id}', '{filters.executer_id}','{order_start_date}','{filters.package_id}', 
        '{filters.order_chat_id}', 'in progress', '{gen_unique_number}');
        """
        self.cursor.execute(query_orders)
        self.connection.commit()

        query_packages = f"""
                UPDATE packages 
                SET status = 'in progress'
                WHERE package_id = {filters.package_id};
                """
        self.cursor.execute(query_packages)
        self.connection.commit()

    def end_work(self, unique_order_number, filters: OfferWorkFilter):
        try:
            order_stop_date = datetime.now()
            query = f"""
            UPDATE orders 
            SET order_finish_date = '{order_stop_date}', status = 'done'
            WHERE unique_order_numner = {unique_order_number} ;
            """
            self.cursor.execute(query)
            self.connection.commit()

            query_packages = f"""
                            UPDATE packages 
                            SET status = 'done'
                            WHERE package_id = {filters.package_id};
                            """
            self.cursor.execute(query_packages)
            self.connection.commit()
        except(Exception, Error) as e:
            LOG.debug('Ошибка окончания заказа', e)


class DBOffersManager:

    @classmethod
    def create_database(cls, user, password, host, port, database):
        engine = create_engine(url=f"postgresql://{user}:{password}@{host}:{port}")
        with Session(engine) as session:
            session.execute(f"create database '{database}' if not exists;")

    def __init__(self, user, password, host, port, database):
#        self.create_database(user, password, host, port, database)
        self.engine = create_engine(url=f"postgresql://{user}:{password}@{host}:{port}/{database.lower()}")
        SQLModel.metadata.create_all(self.engine)

    def close(self):
        pass

    def add_offer(self, offer: OfferInDB):
        with Session(self.engine) as session:
            session.add(offer)
            session.commit()
            session.refresh(offer)
            return offer

    def find_one_offer(self, filters: OfferFilter) -> OfferInDB:
        params = [
            OfferInDB.departure_city == filters.departure_city,
            OfferInDB.destination_country == filters.destination_country
        ]
        if filters.departure_country is not None:
            params.append(OfferInDB.departure_country == filters.departure_country)

        with Session(self.engine) as session:
            statement = select(OfferInDB).where(and_(*params))
            offer: "OfferInDB" = session.exec(statement).first()
            return offer

