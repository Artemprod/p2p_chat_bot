from enum import Enum
from bot_main import TOKEN
from bot_main import bd_password, bd_host, bd_port
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CallbackContext
from telegram import Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import KeyboardButton
import psycopg2
from psycopg2 import Error
import logging
from logs import init_logging

init_logging()

LOG = logging.getLogger(__name__)


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


class UserActionRequest(str,Enum):
    TAKE_ORDER = 'Я хочу взять посылку'
    GIVE_OFFER = 'Я хочу заказать доставку'
    GIVE_RUTE = 'Я хочу разместить свой маршрут'


class ChatStatus(int, Enum):
    ASK_USER_NAME = 1
    ASK_USER_PHONE = 2


class ChatBot:
    def __init__(self, token: str, db_adapter: DBAdapter):
        self.updater = Updater(token=token)
        message_handler = MessageHandler(Filters.text | Filters.contact & (~ Filters.command), self.message_handler)
        # start_command_handler = CommandHandler('start', self.command_start)
        self.updater.dispatcher.add_handler(message_handler)
        # self.updater.dispatcher.add_handler(start_command_handler)
        self.offers = db_adapter.get_offers()

    def start(self):
        self.updater.start_polling()

    def message_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        chat = db_adapter.get_chat(chat_id)
        user = db_adapter.get_user(user_id)
        data_generator = self.data_generator(self.offers)

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
                offer_text = self.data_from_dict_to_text(next(data_generator))
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"{offer_text}", reply_markup=ReplyKeyboardRemove())
                self.next_previous_menu(update)
                db_adapter.update_chat_status(6, update.effective_user.id, update.effective_chat.id)
            elif update.message.text == UserActionRequest.GIVE_OFFER.value:
                pass
            elif update.message.text == UserActionRequest.GIVE_RUTE.value:
                pass
        elif chat_status == 6:
            if update.message.text == 'Следующий заказ':
                offer_text = self.data_from_dict_to_text(next(data_generator))
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"{offer_text}")

    @classmethod
    def command_start(cls, update: Update):
        if update.message.text == '/start':
            update.message.reply_text(
                'Привет, меня зовут бот. Я соеденяю людей и товары по всему миру.\n Давай с тобой познакомимся')
            db_adapter.update_chat_status(1, update.effective_user.id, update.effective_chat.id)
        else:
            pass

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

    @classmethod
    def ask_phone_number(cls, update, context):
        db_adapter.update_phone_number(update.message.contact.phone_number, update.effective_user.id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Записал", reply_markup=ReplyKeyboardRemove())

    @classmethod
    def data_generator(cls, data_list):
        for i in data_list:
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
    def next_previous_menu(cls, update):
        next_order = KeyboardButton('Следующий заказ')
        # give_offer = KeyboardButton('Предыдущий заказ')
        menu_list = [[next_order]]
        markup_main_menu = ReplyKeyboardMarkup(menu_list, resize_keyboard=True)
        update.message.reply_text('показать еще?', reply_markup=markup_main_menu)


if __name__ == "__main__":
    db_adapter = DBAdapter('postgres', bd_password, bd_host, bd_port, 'ChatBot_p2_delivery')
    bot = ChatBot(token=TOKEN, db_adapter=db_adapter)
    bot.start()
