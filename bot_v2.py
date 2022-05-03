import logging
import re
from enum import Enum

import psycopg2
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from db_connectors import (
    ShowOffers, DBAdapter, GiveOffer, OffersInWork, OfferFilter, OfferWorkFilter
)
from logs import init_logging
from secrets import SECRETS

init_logging()

LOG = logging.getLogger(__name__)


class UserOffersActionsRequests(str, Enum):
    NEXT_OFFER = 'Следующий новый заказ'
    PREVIOUS_OFFER = 'Предыдущий заказ'
    TAKE_OFFER = 'Взять заказ'
    NO_OFFERS_MESSAGE = 'Сейчас заказов нет'
    CLOSE_OFFER = 'Закрыть заказ'
    SHOW_MY_OFFERS = 'Посмотреть заказы которые я взял'
    OFFER_IN_PROGRESS = 'Заказы в работе'
    DONE_OFFERS = 'Завершенные заказы'
    BACK_TO_NEW_OFFERS = 'Обратно к новым заказам'
    BACK_TO_MAIN_MENU = 'Обратно в главное меню'


class UserActionRequest(str, Enum):
    TAKE_ORDER = 'Я хочу взять посылку'
    GIVE_OFFER = 'Я хочу заказать доставку'
    GIVE_RUTE = 'Я хочу разместить свой маршрут'
    CHANGE_DESTINATION_CITY = 'Изменить город отправления'
    CHANGE_DEPARTURE_CITY = 'Изменить город прибывания'


class ChatStatus(int, Enum):
    ASK_USER_NAME = 1
    ASK_USER_PHONE = 2
    SHOW_OFFER = 9


class OfferStatus(str, Enum):
    CREATED = 'created'
    COMMUNICATION = 'communication'
    IN_PROGRESS = 'in progress'
    DONE = 'done'


class ChatBot:
    def __init__(self, token: str, bd_password, bd_host, bd_port, db_user: str):
        self.updater = Updater(token=token)
        message_handler = MessageHandler(Filters.text | Filters.contact & (~ Filters.command), self.message_handler)
        # message_handler = MessageHandler(Filters.all, self.message_handler)
        query_handler = CallbackQueryHandler(self.callback_handler)
        self.updater.dispatcher.add_handler(message_handler)
        self.updater.dispatcher.add_handler(query_handler)
        self.generator = self.data_generator
        # self.updater.dispatcher.add_handler(start_command_handler)
        # self.offers = db_adapter.get_offers(
        # start_command_handler = CommandHandler('start', self.command_start)

        self.offers = ShowOffers(
            db_user, bd_password, bd_host, bd_port, 'ChatBot_p2_delivery'
        )
        self.db_adapter = DBAdapter(
            db_user, bd_password, bd_host, bd_port, 'ChatBot_p2_delivery'
        )
        self.give_data = GiveOffer(
            db_user, bd_password, bd_host, bd_port, 'ChatBot_p2_delivery'
        )
        self.offers_in_work = OffersInWork(
            db_user, bd_password, bd_host, bd_port, 'ChatBot_p2_delivery'
        )

    def start(self):
        self.updater.start_polling()

    def close(self):
        for connector in [self.offers, self.db_adapter, self.give_data, self.offers_in_work]:
            try:
                connector.close()
            except psycopg2.Error as ex:
                LOG.error("Failed to close db connector %s: %s", connector, ex)

    def message_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        chat = self.db_adapter.get_chat(chat_id)
        user = self.db_adapter.get_user(user_id)

        if user is None:
            self.db_adapter.create_user(
                first_name=update.effective_user.first_name,
                user_id=update.effective_user.id
            )

        if chat is None:
            self.db_adapter.create_chat(chat_id, user_id)

        self.command_start(update)
        chat_status = self.db_adapter.get_chat_status(chat_id)
        LOG.debug(f"chat_status = {chat_status}")

        if chat_status == ChatStatus.ASK_USER_NAME:
            update.message.reply_text('Как тебя зовут?')
            self.db_adapter.update_chat_status(
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
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"что хочешь сделать?", reply_markup=self.main_menu_keyboard(update))
                self.db_adapter.update_chat_status(5, update.effective_user.id, update.effective_chat.id)

        elif chat_status == 4:  # status of main menu. Show main menu to user
            self.main_menu_keyboard(update)

        elif chat_status == 5:  # main menu handler
            if update.message.text == UserActionRequest.TAKE_ORDER.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"{'С какого города поедешь?'}", reply_markup=ReplyKeyboardRemove())
                self.db_adapter.update_chat_status(6, update.effective_user.id, update.effective_chat.id)

            elif update.message.text == UserActionRequest.GIVE_OFFER.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"{'В каком городе нужно забрать посылку? '}",
                                         reply_markup=ReplyKeyboardRemove())
                self.db_adapter.update_chat_status(12, update.effective_user.id, update.effective_chat.id)
            elif update.message.text == UserActionRequest.GIVE_RUTE.value:
                pass
        elif chat_status == 6:
            self.db_adapter.update_filter('departure_city', update.message.text, update.effective_user.id)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"{'В какой город поедешь? '}")
            self.db_adapter.update_chat_status(7, update.effective_user.id, update.effective_chat.id)
        elif chat_status == 7:
            self.db_adapter.update_filter('destination_city', update.message.text, update.effective_user.id)
            filter_param = self.db_adapter.get_filter(update.effective_user.id)

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"'Показать все заказы из города: {filter_param['departure_city']} "
                                          f"которые нужно доставить в город {filter_param['destination_city']}\n все верно ?",
                                     reply_markup=self.keyboard_boolean(update))

            self.db_adapter.update_chat_status(8, update.effective_user.id, update.effective_chat.id)
        elif chat_status == 8:
            if update.message.text == "Да":
                filters_params = self.db_adapter.get_filter(update.effective_user.id)
                filters = OfferFilter(
                    departure_city=filters_params['departure_city'],
                    destination_country=filters_params['destination_city']
                )
                first_row = self.offers.get_one_row(filters=filters)
                row_dict = self.offers.query_to_dict(first_row)

                if first_row is not None:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"Держи заказы",
                                             reply_markup=self.next_previous_menu())
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"{self.data_from_dict_to_text(row_dict)}",
                                             reply_markup=self.inline_menu_take_order())
                    self.offers.previous_shown_offer(update.effective_user.id, row_dict['package_id'])
                    self.db_adapter.update_chat_status(9, update.effective_user.id, update.effective_chat.id)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"Нет заказов", reply_markup=self.take_order_chose_change_menu())
                    self.db_adapter.update_chat_status(11, update.effective_user.id, update.effective_chat.id)
        elif chat_status == ChatStatus.SHOW_OFFER:
            filters_params = self.db_adapter.get_filter(update.effective_user.id)
            filters = OfferFilter(
                departure_city=filters_params['departure_city'],
                destination_country=filters_params['destination_city']
            )
            if update.message.text == UserOffersActionsRequests.NEXT_OFFER.value:
                package_id = self.offers.get_previous_row_id(update.effective_user.id)
                first_row = self.offers.get_one_row(filters=filters)
                next_offer = self.offers.get_next_row(package_id, filters=filters)

                if next_offer is not None:
                    next_offer_dict = self.offers.query_to_dict(next_offer)
                    package_id = next_offer_dict['package_id']
                    self.offers.previous_shown_offer(update.effective_user.id, package_id)
                    text = self.data_from_dict_to_text(next_offer_dict)
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"{text}",
                                             reply_markup=self.inline_menu_take_order())
                else:
                    row_dict = self.offers.query_to_dict(first_row)
                    self.offers.previous_shown_offer(update.effective_user.id, row_dict['package_id'])
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"Ты посмотрел все новые заказы. сейчас будут по второму кругу")

            elif update.message.text == UserOffersActionsRequests.SHOW_MY_OFFERS.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"Что ты хочешь посмотреть", reply_markup=self.my_work())
                self.db_adapter.update_chat_status(10, update.effective_user.id, update.effective_chat.id)

            elif update.message.text == UserOffersActionsRequests.BACK_TO_MAIN_MENU.value:
                self.db_adapter.update_chat_status(5, update.effective_user.id, update.effective_chat.id)
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"Что ты хочешь сделать'",
                                         reply_markup=self.main_menu_keyboard(update))

        elif chat_status == 10:
            if update.message.text == UserOffersActionsRequests.OFFER_IN_PROGRESS.value:
                if self.db_adapter.get_my_offers(update.effective_user.id):
                    for offer in self.db_adapter.get_my_offers(update.effective_user.id):
                        data_dict = self.db_adapter.query_to_dict_orders(offer)
                        text = self.data_from_dict_to_text_orders(data_dict)
                        context.bot.send_message(chat_id=update.effective_chat.id,
                                                 text=f"{text}", reply_markup=self.inline_menu_close_order())
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"Нету заказов в работе")

            elif update.message.text == UserOffersActionsRequests.DONE_OFFERS.value:
                finished_offers = self.db_adapter.get_finished_offers()
                for offer in finished_offers:
                    query_dict = self.db_adapter.query_to_dict_finishd_orders(offer)
                    text = self.data_from_dict_to_text_finished_orders(query_dict)
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"{text}")
            elif update.message.text == UserOffersActionsRequests.BACK_TO_NEW_OFFERS.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"Жми кнопку 'Следующий закз "
                                              f"чтобы посмотреть новые заказы если они есть '",
                                         reply_markup=self.next_previous_menu())
                self.db_adapter.update_chat_status(9, update.effective_user.id, update.effective_chat.id)

            elif update.message.text == UserOffersActionsRequests.BACK_TO_MAIN_MENU.value:
                self.db_adapter.update_chat_status(5, update.effective_user.id, update.effective_chat.id)
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"Что ты хочешь сделать'",
                                         reply_markup=self.main_menu_keyboard(update))

        elif chat_status == 11:
            if update.message.text == UserOffersActionsRequests.BACK_TO_MAIN_MENU.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"Что ты хочешь сделать'",
                                         reply_markup=self.main_menu_keyboard(update))
                self.db_adapter.update_chat_status(5, update.effective_user.id, update.effective_chat.id)

            elif update.message.text == UserActionRequest.CHANGE_DEPARTURE_CITY.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"{'С какого города поедешь?'}",
                                         reply_markup=ReplyKeyboardRemove())
                self.db_adapter.update_chat_status(6, update.effective_user.id, update.effective_chat.id)

            elif update.message.text == UserActionRequest.CHANGE_DESTINATION_CITY.value:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"В какой город поедешь?''",
                                         reply_markup=ReplyKeyboardRemove())
                self.db_adapter.update_chat_status(7, update.effective_user.id, update.effective_chat.id)

            elif chat_status == 12:
                pass

    def command_start(self, update: Update):
        if update.message.text == '/start':
            update.message.reply_text(
                'Привет, меня зовут бот. Я соединяю людей и товары по всему миру.\n Давай с тобой познакомимся')
            self.db_adapter.update_chat_status(1, update.effective_user.id, update.effective_chat.id)
        else:
            pass

    def callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        answer = query.data
        filters_params = self.db_adapter.get_filter(update.effective_user.id)
        filters = OfferFilter(
            departure_city=filters_params['departure_city'],
            destination_country=filters_params['destination_city']
        )
        package_id = self.offers.get_previous_row_id(update.effective_user.id)
        offer_user_id = self.offers.get_user_id_by_package(package_id)
        user = self.db_adapter.get_user(offer_user_id)

        filters = OfferWorkFilter(
           costumer_id=offer_user_id,
           executer_id=update.effective_user.id,
           package_id=package_id,
           order_chat_id=update.effective_chat.id
        )

        if answer == UserOffersActionsRequests.TAKE_OFFER.value:
            query.answer()
            name = user[1]
            phone = user[4]
            check_tuple = (update.effective_user.id, offer_user_id, package_id)

            if self.offers_in_work.check_working(filters=filters) != check_tuple:

                context.bot.send_contact(update.effective_chat.id, phone, name,
                                         reply_markup=self.inline_menu_close_order())
                self.offers_in_work.star_work(filters=filters)
            else:
                pass
        elif answer == UserOffersActionsRequests.CLOSE_OFFER.value:
            query.answer()
            text = query.message.text
            uique_id = self.serch_unique_id(text)
            self.offers_in_work.end_work(uique_id, filters=filters)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Закрыт")

    def validate_name(self, update, context):
        name = update.message.text
        if len(name) > 100:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Ты думаешь это смешно?")
            self.keyboard_boolean(update)
            self.db_adapter.update_chat_status(1, update.effective_user.id, update.effective_chat.id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Очень приятно познакомиться {update.message.text}")
            self.db_adapter.update_user_name(name, update.effective_user.id)
            self.db_adapter.update_chat_status(3, update.effective_user.id, update.effective_chat.id)

    def serch_unique_id(self, text):
        reg_template_text = 'Уникальный ID заказа:(\s+\d+|\d+)'
        reg_template_digit = '\d+'
        result_1 = re.findall(reg_template_text, text)
        result_2 = re.findall(reg_template_digit, str(result_1[0]))[0]
        return int(result_2)

    def ask_phone_number(self, update, context):
        self.db_adapter.update_phone_number(update.message.contact.phone_number, update.effective_user.id)
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
        # give_rute = KeyboardButton(UserActionRequest.GIVE_RUTE.value)
        menu_list = [[give_offer, take_order]]
        markup_main_menu = ReplyKeyboardMarkup(menu_list, resize_keyboard=True)
        return markup_main_menu

    @classmethod
    def take_order_chose_change_menu(cls, ):
        main_menu = KeyboardButton(UserOffersActionsRequests.BACK_TO_MAIN_MENU.value)
        change_departue_city = KeyboardButton(UserActionRequest.CHANGE_DEPARTURE_CITY.value)
        change_destanation_city = KeyboardButton(UserActionRequest.CHANGE_DESTINATION_CITY.value)

        # give_rute = KeyboardButton(UserActionRequest.GIVE_RUTE.value)
        menu_list = [[main_menu], [change_departue_city, change_destanation_city]]
        markup_main_menu = ReplyKeyboardMarkup(menu_list, resize_keyboard=True)
        return markup_main_menu

    @classmethod
    def next_previous_menu(cls):
        next_order = KeyboardButton(UserOffersActionsRequests.NEXT_OFFER.value)
        show_my_offers = KeyboardButton(UserOffersActionsRequests.SHOW_MY_OFFERS.value)
        back_to_main_menu = back_to_main_menu = KeyboardButton(UserOffersActionsRequests.BACK_TO_MAIN_MENU.value)
        menu_list = [[next_order, show_my_offers], [back_to_main_menu]]
        markup_main_menu = ReplyKeyboardMarkup(menu_list, resize_keyboard=True)
        return markup_main_menu

    @classmethod
    def my_work(cls):
        offer_in_progress = KeyboardButton(UserOffersActionsRequests.OFFER_IN_PROGRESS.value)
        done_offers = KeyboardButton(UserOffersActionsRequests.DONE_OFFERS.value)
        back_to_new_offers = KeyboardButton(UserOffersActionsRequests.BACK_TO_NEW_OFFERS.value)
        back_to_main_menu = KeyboardButton(UserOffersActionsRequests.BACK_TO_MAIN_MENU.value)
        menu_list = [[offer_in_progress, done_offers], [back_to_new_offers, back_to_main_menu]]
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
    bot = ChatBot(
        token=SECRETS.token,
        bd_password=SECRETS.bd_password,
        bd_host=SECRETS.bd_host,
        bd_port=SECRETS.bd_port,
        db_user=SECRETS.bd_user
    )
    try:
        bot.start()
    finally:
        bot.close()
