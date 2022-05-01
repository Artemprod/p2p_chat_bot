from enum import Enum
from bot_main import TOKEN
from bot_main import bd_password, bd_host, bd_port
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CallbackContext
from telegram import Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import KeyboardButton
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
import psycopg2
from psycopg2 import Error
import logging
from logs import init_logging
from datetime import datetime
import re




init_logging()

LOG = logging.getLogger(__name__)


class UserOffersActionsRequests(str, Enum):
    NEXT_OFFER = 'Следующий новый заказ'
    PREVIOUS_OFFER = 'Предыдущий заказ'
    TAKE_OFFER = 'Взять заказ'
    NO_OFFERS_MESSAGE = 'Сейчас заказов нет'
    CLOSE_OFFER = 'Закрыть заказ'
    SHOW_MY_OFFERS ='Посмотреть заказы которые я взял'
    OFFER_IN_PROGRESS ='Заказы в работе'
    DONE_OFFERS = 'Завершенные заказы'


class UserActionRequest(str, Enum):
    TAKE_ORDER = 'Я хочу взять посылку'
    GIVE_OFFER = 'Я хочу заказать доставку'
    GIVE_RUTE = 'Я хочу разместить свой маршрут'


class ChatStatus(int, Enum):
    ASK_USER_NAME = 1
    ASK_USER_PHONE = 2


class OfferStatus(str, Enum):
    CREATED = 'created'
    COMMUNICATION = 'communication'
    IN_PROGRESS = 'in progress'
    DONE = 'done'


class DBAdapter:  # responsible for Users and Chats
    def __init__(self, user, password, host, port, database):
        try:
            self.connection = psycopg2.connect(user=user,
                                               password=password,
                                               host=host,
                                               port=port,
                                               database=database)
            self.cursor = self.connection.cursor()
            LOG.debug("Соединение с базой установлено")
        except(Exception, Error) as e:
            LOG.error("Ошибка работы с базой:", e)

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
        except(Exception,Error) as e:
            LOG.debug('Ошибка в выдаче завершенных закзаов',e )
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



class ShowOffers(DBAdapter):
    def __init__(self, user, password, host, port, database, departure_city, destination_country):
        super().__init__(user, password, host, port, database)
        self.departure_city = departure_city
        self.destination_country = destination_country

    def count_rows(self):
        count = f"""
                SELECT 
                        COUNT(*)
                FROM packages as p
                LEFT JOIN public.users as u on u.user_id = p.custumer_user_id
                WHERE status = 'created' and  departure_city ='{self.departure_city}'
                and  destination_country = '{self.destination_country}';"""
        self.cursor.execute(count)
        self.connection.commit()
        result = self.cursor.fetchall()
        return result[0][0]

    def get_one_row(self):
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
                    WHERE status = 'created' and  departure_city ='{self.departure_city}'
                    and  destination_country = '{self.destination_country}' 
                    ORDER BY package_id
                    LIMIT 1 
    """
        self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
        return result

    def get_next_row(self, package_id):
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
                    WHERE status = 'created' and  departure_city ='{self.departure_city}'
                    and  destination_country = '{self.destination_country}' and package_id > {package_id}
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

    def previous_shown_offer(self, user_id, packeg_id):
        try:
            select_query = f"""
            SELECT * FROM shown_offers
            WHERE user_id = {user_id}
    """
            self.cursor.execute(select_query)
            self.connection.commit()
            result = self.cursor.fetchone()

            if result == None:
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
                SELECT 
                    package_id 
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
            LOG.debug('Ошибка извлечеия ID пользователя по ID посылки')

class OfferWork(DBAdapter):
    def __init__(self,user, password, host, port, database, costumer_id, executer_id, package_id, chat_id):
        super().__init__(user, password, host, port, database,)
        self.costumer_id = costumer_id
        self.executer_id = executer_id
        self.package_id = package_id
        self.order_chat_id = chat_id

    def check_working(self):
        query = f"""
               SELECT 
               costumer_id,
               executor_id, 
               package_id
               FROM orders
               WHERE costumer_id ={self.costumer_id} and  executor_id = {self.executer_id} and package_id ={self.package_id}
                ;
               """
        self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
        return result

    def check_unique_id(self):
        query = f"""
                       SELECT 
                       unique_order_numner
                       FROM orders
                       WHERE costumer_id ={self.costumer_id} and  executor_id = {self.executer_id} and package_id ={self.package_id}
                        ;
                       """
        self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
        return result

    def star_work(self):


        gen_unique_number = f"{self.package_id}{datetime.now().time().minute}{datetime.now().time().second}"
        order_start_date = datetime.now()
        query_orders = f"""
        INSERT INTO orders ( costumer_id, executor_id, order_start_date, package_id, order_chat_id, status, unique_order_numner)
        VALUES ('{self.costumer_id}', '{self.executer_id}','{order_start_date}','{self.package_id}', '{self.order_chat_id}', 'in progress', '{gen_unique_number}');
        """
        self.cursor.execute(query_orders )
        self.connection.commit()

        query_packages =f"""
                UPDATE packages 
                SET status = 'in progress'
                WHERE package_id = {self.package_id};
                """
        self.cursor.execute(query_packages)
        self.connection.commit()



    def end_work(self, unique_order_number):
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
                            WHERE package_id = {self.package_id};
                            """
            self.cursor.execute(query_packages)
            self.connection.commit()
        except(Exception, Error) as e:
            LOG.debug('Ошибка окончания заказа', e)


class ChatBot:
    def __init__(self, token: str, db_adapter: DBAdapter):
        self.updater = Updater(token=token)
        # message_handler = MessageHandler(Filters.text | Filters.contact & (~ Filters.command) , self.message_handler)
        message_handler = MessageHandler(Filters.all, self.message_handler)
        query_handler = CallbackQueryHandler(self.callback_handler)
        self.updater.dispatcher.add_handler(message_handler)
        self.updater.dispatcher.add_handler(query_handler)
        self.generator = self.data_generator
        # self.updater.dispatcher.add_handler(start_command_handler)
        # self.offers = db_adapter.get_offers(
        # start_command_handler = CommandHandler('start', self.command_start)

    def start(self):
        self.updater.start_polling()

    def message_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        chat = db_adapter.get_chat(chat_id)
        user = db_adapter.get_user(user_id)

        if user is None:
            db_adapter.create_user(
                first_name=update.effective_user.first_name,
                user_id=update.effective_user.id
            )

        if chat is None:
            db_adapter.create_chat(chat_id, user_id)

        self.command_start(update)
        chat_status = db_adapter.get_chat_status(chat_id)
        LOG.debug(f"chat_status = {chat_status}")

        if chat_status == ChatStatus.ASK_USER_NAME:
            update.message.reply_text('Как тебя зовут?')
            db_adapter.update_chat_status(
                new_status=ChatStatus.ASK_USER_PHONE.value,
                user_id=update.effective_user.id,
                chat_id=update.effective_chat.id
            )
        elif chat_status == ChatStatus.ASK_USER_PHONE:
            self.validate_name(update, context)
            update.message.reply_text('Напиши свой номер телефона')
            self.keyboard_contact(update, context)

        elif chat_status == 3:
            self.ask_phone_number(update, context)
            if update.message.contact.phone_number:
                self.main_menu_keyboard(update)
                db_adapter.update_chat_status(5, update.effective_user.id, update.effective_chat.id)

        elif chat_status == 4:  # status of main menu. Show main menu to user
            self.main_menu_keyboard(update)

        elif chat_status == 5:  # main menu handler
            if update.message.text == UserActionRequest.TAKE_ORDER.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"{'С какого города поедешь?'}", reply_markup=ReplyKeyboardRemove())
                db_adapter.update_chat_status(6, update.effective_user.id, update.effective_chat.id)


            elif update.message.text == UserActionRequest.GIVE_OFFER.value:
                pass
            elif update.message.text == UserActionRequest.GIVE_RUTE.value:
                pass
        elif chat_status == 6:
            db_adapter.update_filter('departure_city', update.message.text, update.effective_user.id)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"{'В какой город поедешь? '}")
            db_adapter.update_chat_status(7, update.effective_user.id, update.effective_chat.id)
        elif chat_status == 7:
            db_adapter.update_filter('destination_city', update.message.text, update.effective_user.id)
            filter_param = db_adapter.get_filter(update.effective_user.id)

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"'Показать все заказы из города: {filter_param['departure_city']} "
                                          f"которые нужно доставить в город {filter_param['destination_city']}\n все верно ?",
                                     reply_markup=self.keyboard_boolean(update))

            db_adapter.update_chat_status(8, update.effective_user.id, update.effective_chat.id)
        elif chat_status == 8:
            if update.message.text == "Да":
                filters_params = db_adapter.get_filter(update.effective_user.id)
                offers = ShowOffers('postgres', bd_password, bd_host, bd_port,
                                    'ChatBot_p2_delivery', departure_city=filters_params['departure_city'],
                                    destination_country=filters_params['destination_city'])
                first_row = offers.get_one_row()
                row_dict = offers.query_to_dict(first_row)

                if first_row != None:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"Держи заказы",
                                             reply_markup=self.next_previous_menu())
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"{self.data_from_dict_to_text(row_dict)}",
                                             reply_markup=self.inline_menu_take_order())
                    offers.previous_shown_offer(update.effective_user.id, row_dict['package_id'])
                    db_adapter.update_chat_status(9, update.effective_user.id, update.effective_chat.id)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"Нет заказов")
        elif chat_status == 9:
            filters_params = db_adapter.get_filter(update.effective_user.id)
            offers = ShowOffers('postgres', bd_password, bd_host, bd_port, 'ChatBot_p2_delivery',
                                departure_city=filters_params['departure_city'],
                                destination_country=filters_params['destination_city'])

            if update.message.text == UserOffersActionsRequests.NEXT_OFFER.value:
                package_id = offers.get_previous_row_id(update.effective_user.id)
                first_row = offers.get_one_row()
                next_offer = offers.get_next_row(package_id)

                if next_offer != None:
                    next_offer_dict = offers.query_to_dict(next_offer)
                    package_id = next_offer_dict['package_id']
                    offers.previous_shown_offer(update.effective_user.id, package_id)
                    text = self.data_from_dict_to_text(next_offer_dict)
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"{text}",
                                             reply_markup=self.inline_menu_take_order())
                else:
                    row_dict = offers.query_to_dict(first_row)
                    offers.previous_shown_offer(update.effective_user.id, row_dict['package_id'])
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"Ты посомотрел все новые заказы. сейчас будут по второму кругу")

            elif update.message.text == UserOffersActionsRequests.SHOW_MY_OFFERS.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"Что ты хочешь посмотреть", reply_markup=self.my_work())
                db_adapter.update_chat_status(10, update.effective_user.id, update.effective_chat.id)

        elif chat_status == 10:

            if update.message.text == UserOffersActionsRequests.OFFER_IN_PROGRESS.value:
                for i in db_adapter.get_my_offers(update.effective_user.id):
                    data_dict = db_adapter.query_to_dict_orders(i)
                    text = self.data_from_dict_to_text_orders(data_dict)
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"{text}", reply_markup=self.inline_menu_close_order())



            elif update.message.text == UserOffersActionsRequests.DONE_OFFERS.value:
                offers = db_adapter.get_finished_offers()
                for i in offers:
                    query_dict = db_adapter.query_to_dict_finishd_orders(i)
                    text = self.data_from_dict_to_text_finished_orders(query_dict)
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"{text}")



    @classmethod
    def command_start(cls, update: Update):
        if update.message.text == '/start':
            update.message.reply_text(
                'Привет, меня зовут бот. Я соеденяю людей и товары по всему миру.\n Давай с тобой познакомимся')
            db_adapter.update_chat_status(1, update.effective_user.id, update.effective_chat.id)
        else:
            pass

    def callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        answer = query.data
        filters_params = db_adapter.get_filter(update.effective_user.id)
        offers = ShowOffers('postgres', bd_password, bd_host, bd_port, 'ChatBot_p2_delivery',
                            departure_city=filters_params['departure_city'],
                            destination_country=filters_params['destination_city'])

        package_id = offers.get_previous_row_id(update.effective_user.id)
        offer_user_id = offers.get_user_id_by_package(package_id)
        user = db_adapter.get_user(offer_user_id)
        offer_work = OfferWork('postgres', bd_password, bd_host, bd_port, 'ChatBot_p2_delivery',
                               costumer_id=offer_user_id,
                               executer_id=update.effective_user.id,
                               package_id=package_id,
                               chat_id=update.effective_chat.id)

        if answer == UserOffersActionsRequests.TAKE_OFFER.value:
            query.answer()
            name = user[1]
            phone = user[4]
            check_tuple = (update.effective_user.id, offer_user_id,package_id)

            if offer_work.check_working() != check_tuple:

                context.bot.send_contact(update.effective_chat.id, phone, name, reply_markup=self.inline_menu_close_order())
                offer_work.star_work()
            else:
                pass
        elif answer == UserOffersActionsRequests.CLOSE_OFFER.value:
            query.answer()
            text = query.message.text
            uique_id = self.serch_unique_id(text)
            offer_work.end_work(uique_id)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Закрыт")








    def validate_name(self, update, context):
        name = update.message.text
        if len(name) > 100:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Ты думаешь это смешно?")
            self.keyboard_boolean(update)
            db_adapter.update_chat_status(1, update.effective_user.id, update.effective_chat.id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Очень приятно познакомиться {update.message.text}")
            db_adapter.update_user_name(name, update.effective_user.id)
            db_adapter.update_chat_status(3, update.effective_user.id, update.effective_chat.id)

    def serch_unique_id(self, text):
        reg_template_text = 'Уникальный ID заказа:(\s+\d+|\d+)'
        reg_template_digit = '\d+'
        result_1 = re.findall(reg_template_text, text)
        result_2 = re.findall(reg_template_digit, str(result_1[0]))[0]
        return int(result_2)




    @classmethod
    def ask_phone_number(cls, update, context):
        db_adapter.update_phone_number(update.message.contact.phone_number, update.effective_user.id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Записал", reply_markup=ReplyKeyboardRemove())

    @classmethod
    def data_generator(cls, data):
        for i in range(data):
            yield i

    @classmethod
    def data_from_dict_to_text(cls, data):
        text = f"""                              
Что нужно сделать:{data['title']}        
Кто просит {data['user_name']}           
Откуда забрать                           
            Страна: {data['departure_country']}  
            Город:  {data['departure_city']}     
Куда привезти                            
            Страна: {data['destination_country']}
            Город:  {data['destination_city']}   
Стоимость: {data['price']} рублей        
Описание: {data['description']}          


    """
        print()
        return text

    @classmethod
    def data_from_dict_to_text_orders(cls, data):
        text = f"""                              
    Что нужно сделать:{data['title']}        
    Кто просит {data['user_name']}           
    Откуда забрать                           
                Страна: {data['departure_country']}  
                Город:  {data['departure_city']}     
    Куда привезти                            
                Страна: {data['destination_country']}
                Город:  {data['destination_city']}   
    Стоимость: {data['price']} рублей        
    Описание: {data['description']}          
    Уникальный ID заказа: {data['unique_order_numner']}
        """
        return text


    @classmethod
    def data_from_dict_to_text_finished_orders(cls, data):
        text = f"""                              
    Что нужно было сделать: {data['title']}        
    Кто просил: {data['user_name']}           
    Откуда забрал                          
                Страна: {data['departure_country']}  
                Город:  {data['departure_city']}     
    Куда привез                           
                Страна: {data['destination_country']}
                Город:  {data['destination_city']}   
    Стоимость этого заказа была: {data['price']} рублей        
    Описание: {data['description']}          
    Когда взял заказ: {data['order_start_date']}
    Когда закончил: {data['order_finish_date']}
        """
        return text



    @classmethod
    def keyboard_boolean(cls, update):
        keyboard = [['Да', 'Нет']]
        markup_boolean = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, row_width=1, resize_keyboard=True)
        update.message.reply_text("Выбери ответ", reply_markup=markup_boolean)

    @classmethod
    def keyboard_contact(cls, update, context):
        button = [[KeyboardButton('Отправить контакт', request_contact=True)]]
        markup_contact = ReplyKeyboardMarkup(button, one_time_keyboard=True, row_width=1, resize_keyboard=True)
        update.message.reply_text('Нажми на кнопку, чтобы отправить контакт', reply_markup=markup_contact)

    @classmethod
    def main_menu_keyboard(cls, update):
        take_order = KeyboardButton(UserActionRequest.TAKE_ORDER.value)
        give_offer = KeyboardButton(UserActionRequest.GIVE_OFFER.value)
        give_rute = KeyboardButton(UserActionRequest.GIVE_RUTE.value)
        menu_list = [[give_offer], [take_order, give_rute]]
        markup_main_menu = ReplyKeyboardMarkup(menu_list, resize_keyboard=True)
        update.message.reply_text('Что ты хочешь сделать?', reply_markup=markup_main_menu)

    @classmethod
    def next_previous_menu(cls):
        next_order = KeyboardButton(UserOffersActionsRequests.NEXT_OFFER.value)
        show_my_offers = KeyboardButton(UserOffersActionsRequests.SHOW_MY_OFFERS.value)
        # give_offer = KeyboardButton('Предыдущий заказ')
        menu_list = [[next_order], [show_my_offers]]
        markup_main_menu = ReplyKeyboardMarkup(menu_list, resize_keyboard=True)
        return markup_main_menu

    @classmethod
    def my_work(cls):
        offer_in_progress = KeyboardButton(UserOffersActionsRequests.OFFER_IN_PROGRESS.value)
        done_offers = KeyboardButton(UserOffersActionsRequests.DONE_OFFERS.value)
        menu_list = [[offer_in_progress, done_offers]]
        markup_main_menu = ReplyKeyboardMarkup(menu_list, resize_keyboard=True)
        return markup_main_menu

    @classmethod
    def inline_menu_take_order(cls):
        # next_offer = InlineKeyboardButton(UserOffersActionsRequests.NEXT_OFFER.value, callback_data=1)
        take_offer = InlineKeyboardButton(UserOffersActionsRequests.TAKE_OFFER.value,
                                          callback_data=UserOffersActionsRequests.TAKE_OFFER.value)
        # previous_offer = InlineKeyboardButton(UserOffersActionsRequests.PREVIOUS_OFFER.value, callback_data=3)
        buttons_list = [[take_offer]]
        markup_inline_offers_menu = InlineKeyboardMarkup(buttons_list)
        return markup_inline_offers_menu

    @classmethod
    def inline_menu_close_order(cls):
        close_offer = InlineKeyboardButton(UserOffersActionsRequests.CLOSE_OFFER.value,
                                          callback_data=UserOffersActionsRequests.CLOSE_OFFER.value)
        buttons_list = [[close_offer]]
        markup_inline_close_menu = InlineKeyboardMarkup(buttons_list)
        return markup_inline_close_menu

if __name__ == "__main__":
    db_adapter = DBAdapter('postgres', bd_password, bd_host, bd_port, 'ChatBot_p2_delivery')
    bot = ChatBot(token=TOKEN, db_adapter=db_adapter)
    bot.start()
