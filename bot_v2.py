from bot_main import TOKEN
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram.ext import CallbackContext
from telegram import Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import re




class ChatBot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        message_handler = MessageHandler(Filters.text & (~Filters.command), self.message_handler)
        self.start_command_handler = CommandHandler('start', self.command_start)
        self.updater.dispatcher.add_handler(message_handler)
        self.updater.dispatcher.add_handler(self.start_command_handler)




    def start(self):
        self.updater.start_polling()

    def command_start(self,update:Update, context:CallbackContext):
        context.bot.send_message(chat_id = update.effective_chat.id, text = 'Привет, меня зовут бот. А тебя как?')



    def message_handler(self, update:Update, context:CallbackContext):
        print(update.message)
        self.validate_name(update, context)
        print(update.effective_message)

        # context.bot.send_message(chat_id=update.effective_chat.id,text="Напиши свой номер телефона")



    def validate_name(self, update, context):
        text = update.message.text
        if len(text) > 100:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="я в первый раз вижу такое длинное имя, тебя действительно так зовут?")
            self.keybord_boolen(update)

            if update.message.text == 'Да':
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='Очень интересно, запишу в свою память и напишу об этом статью на Википедию',
                                         reply_markup=ReplyKeyboardRemove())

            elif update.message.text == 'Нет':
                name = update.message.chat.first_name
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f'Я так и понял, тебя ведь зовут {name}',
                                         reply_markup=ReplyKeyboardRemove())

        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Очень приятно познакомиться {text}')


    def keybord_boolen(self, update):
        keybord = [['Да', 'Нет']]
        markup_boolen = ReplyKeyboardMarkup(keybord, one_time_keyboard=True)
        update.message.reply_text("Выбери ответ", reply_markup=markup_boolen)

    def phone_number(self, update):
        pass


if __name__ == "__main__":
    bot = ChatBot(TOKEN)
    bot.start()
