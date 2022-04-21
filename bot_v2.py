from bot_main import TOKEN
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram.ext import CallbackContext
from telegram import Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import KeyboardButton
import psycopg2
from psycopg2 import Error
import re

class DBAdapter:  # responsible for Users and Chats
    def __init__(self, user, password, host, port, database):
        try:
            self.connection = psycopg2.connect(user=user,
                                               password = password,
                                               host = host,
                                               port = port,
                                               database = database)
            self.cursor = self.connection.cursor()
            print("Соединение с базой установлно")
        except(Exception, Error) as e:
            print("Ошибка работы с базой:", e)


    def create_user(self,
                    first_name:str,
                    user_id:int,
                    nick_name = None,
                    last_name = None,
                    phone_number = None,
                    email = None):

        try:
            create_user_query = f"""
            INSERT INTO users ("UserName", "UserLastName", "UserNickName","Email", "PhoneNumber", user_id)
            VALUES ('{first_name}',' {last_name}','{nick_name}','{email}', '{phone_number}','{user_id}')
            """
            self.cursor.execute(create_user_query)
            self.connection.commit()
            print("Пользователь добавлен в базу")

        except(Exception, Error) as e:
            print("Ошибка работы с базой:", e)

    def ubpdate_phone_number(self, phone_number,user_id):
        try:
            update_query = f"""
                UPDATE users SET "PhoneNumber" = '{phone_number}'
                WHERE user_id = {user_id};
                """
            self.cursor.execute(update_query)
            self.connection.commit()
            print(f"Телефон пользователя изменен на {phone_number}")
        except(Exception, Error) as e:
            print("Ошибка при обновление телефонного номера:", e)

    def change_nick(self):
        pass

    def get_user(self, user_id) -> dict:
        try:
            select_query = f"""
            SELECT * 
            FROM users
            WHERE user_id= {user_id} 
            """
            self.cursor.execute(select_query)
            result = self.cursor.fetchone()
            return result
        except(Exception, Error) as e:
            print("Ошибка при получение данных пользователя:", e)

    def update_user_name(self,name,user_id):
        try:
            update_query =f"""
                UPDATE users SET "UserName" = '{name}'
                WHERE user_id = {user_id};
                """
            self.cursor.execute(update_query)
            self.connection.commit()
            print(f"Имя пользователя изменено на {name}")
        except(Exception, Error) as e:
            print("Ошибка при обновлении имени:", e)

    def create_chat(self, chat_id, user_id):
        try:
            create_chat_query = f"""
            INSERT INTO user_chat (chat_id, user_id)
            VALUES ({chat_id},{user_id});
            """
            self.cursor.execute(create_chat_query)
            self.connection.commit()
            print(f"новый чат № {chat_id}  для пользователя {user_id} создан")
        except(Exception,Error) as e:
            print("Ошибка при создании нового чата:", e)

    def update_chat_status(self, new_status, user_id, chat_id):
        try:
            update_chat_query = f"""
            UPDATE user_chat SET "ChatStatus" = {new_status}
            WHERE chat_id = {chat_id} AND user_id = {user_id};
            """
            self.cursor.execute(update_chat_query)
            self.connection.commit()
            print(f"Статус чата: {chat_id} для пользователя: {user_id} обновлен. Статус чата: {new_status}")
        except(Exception, Error) as e:
            print("Ошибка при обновлении статуса :", e)


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
            print("Ошибка при получении данных о чате:", e)

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
            print("Ошибка при получении статутса чата:", e)






class ChatBot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        message_handler = MessageHandler(Filters.text | Filters.contact & (~ Filters.command), self.message_handler)
        # start_command_handler = CommandHandler('start', self.command_start)
        self.updater.dispatcher.add_handler(message_handler)
        # self.updater.dispatcher.add_handler(start_command_handler)


    def start(self):
        self.updater.start_polling()


    def message_handler(self, update:Update, context:CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        chat = db_adapter.get_chat(chat_id)
        user = db_adapter.get_user(user_id)



        if user == None:
            db_adapter.create_user(update.effective_user.first_name, update.effective_user.id)
        if chat == None:
            db_adapter.create_chat(chat_id, user_id)

        self.command_start(update)
        chat_status = db_adapter.get_chat_status(chat_id)
        print(chat_status)

        if chat_status == 1:
            update.message.reply_text('Как тебя зовут? ')
            db_adapter.update_chat_status(2, update.effective_user.id, update.effective_chat.id)
        elif chat_status == 2:
            self.validate_name(update, context)
            update.message.reply_text('Напиши свой номер телефона')
            self.keybord_contact(update, context)
        elif chat_status == 3:
            self.ask_phone_number(update, context)
        elif chat_status == 4:
            pass

        # elif chat_status == 4:
        #     self.ask_phone_number(update, context)
        #
        # elif chat_status == 5:
        #     context.bot.send_message(chat_id=update.effective_chat.id, text='Супер, телефон сохранен',
        #                              reply_markup=ReplyKeyboardRemove())
        #     db_adapter.update_chat_status(6, update.effective_user.id, update.effective_chat.id)
        # elif chat_status == 6:
        #     pass





    def command_start(self,update:Update):
        if update.message.text == '/start':
            update.message.reply_text('Привет, меня зовут бот. Я соеденяю людей и товары по всему миру.\n Давай с тобой познакомимся')
            db_adapter.update_chat_status(1, update.effective_user.id, update.effective_chat.id)
        else:
            pass


    def validate_name(self, update, context):
        name = update.message.text
        if len(name) > 100:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Ты думаешь это смешно?")
            self.keybord_boolen(update)
            db_adapter.update_chat_status(1, update.effective_user.id, update.effective_chat.id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Очень приятно познакомиться {update.message.text}")
            db_adapter.update_user_name(name, update.effective_user.id)
            db_adapter.update_chat_status(3, update.effective_user.id, update.effective_chat.id)


    def ask_phone_number(self, update,context):
        db_adapter.ubpdate_phone_number(update.message.contact.phone_number,update.effective_user.id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Записал", reply_markup= ReplyKeyboardRemove())
        db_adapter.update_chat_status(4, update.effective_user.id, update.effective_chat.id)


    def keybord_boolen(self, update):
        keybord = [['Да', 'Нет']]
        markup_boolen = ReplyKeyboardMarkup(keybord, one_time_keyboard=True, row_width=1, resize_keyboard=True)
        update.message.reply_text("Выбери ответ", reply_markup=markup_boolen)

    def keybord_contact(self,update,context):
        button = [[KeyboardButton('Отправить контакт', request_contact=True)]]
        markup_contact = ReplyKeyboardMarkup(button,one_time_keyboard=True, row_width=1, resize_keyboard=True )
        update.message.reply_text('Нажми на кнопку, чтобы отправить контакт', reply_markup=markup_contact)

    def main_menu_keyboard(self,update,context):
        pass





if __name__ == "__main__":
    bot = ChatBot(TOKEN)
    bot.start()
    db_adapter = DBAdapter('postgres','Portnov1991', '127.0.0.1','5432', 'ChatBot_p2_delivery')


