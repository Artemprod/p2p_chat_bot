from apscheduler.schedulers.blocking import BlockingScheduler
from amplitude import Amplitude,BaseEvent
key = '19c426154fc175a66e0852b9ac0a2710'

class EventTracker:

    def __init__(self, key):
        self.client = Amplitude(key)

    def amplitude_authorizetion(self):

        self.client.track(BaseEvent(
            event_type='Python Event',
            user_id='datamonster@gmail.com',
            ip='127.0.0.1',
            event_properties={
                'keyString': 'valueString',
                'keyInt': 11,
                'keyBool': True
            }
        ))


    def launch_first_time(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="first_time_launched",
                user_id=user_id,
                time=time
            ))

    def session_start(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="session_start",
                user_id=user_id,
                time=time
            ))

    def make_order_chosen(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="make_order_chosen",
                user_id=user_id,
                time=time
            ))

    def take_order_chosen(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="take_order_chosen",
                user_id=user_id,
                time=time
            ))

    def make_order_messeged_departure_city(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="messeged_departure_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))


    def make_order_make_mistake_departure_city(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="make_order_make_mistake_departure_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_corected_by_list_departure_city(self, user_id, time, button_type):
        self.client.track(
            BaseEvent(
                event_type="make_order_corected_by_list_departure_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'type_of_button': button_type
                }
            ))

    def make_order_departure_city_corection_messaged(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="make_order_departure_city_messaged",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_messeged_destination_city(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="messeged_destination_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_make_mistake_destanation_city(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="make_order_make_mistake_destanation_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_corected_by_list_destenation_city(self, user_id, time, button_type):
        self.client.track(
            BaseEvent(
                event_type="make_order_corected_by_list_destenation_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'type_of_button': button_type
                }
            ))

    def make_order_destanation_city_corection_messaged(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="make_order_destanation_city_messaged",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_calendar_watched(self, user_id, time, type_of_date):
        self.client.track(
            BaseEvent(
                event_type="make_order_calendar_watched",
                user_id=user_id,
                time=time,
                event_properties={
                    'type_of_date': type_of_date
                }
            ))

    def make_order_data_messaged(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="make_order_data_messaged",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_package_title_writed(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="make_order_package_title_writed",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_price_error(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="make_order_price_error",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def make_order_informftion_confermed(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="make_order_informftion_confermed",
                user_id=user_id,
                time=time
            ))

    def make_order_user_flow_finished(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="make_order_user_flow_finished",
                user_id=user_id,
                time=time
            ))

    def make_order_order_created(self, user_id, time, order_id, created_date, price, departure_city,
                                 destanation_city, order_type, description):
        self.client.track(
            BaseEvent(
                event_type="make_order_order_created",
                user_id=user_id,
                time=time,
                event_properties={
                    'order_id': order_id,
                    'created_date': created_date,
                    'price': price,
                    'departure_city': departure_city,
                    'destanation_city': destanation_city,
                    'order_type': order_type,
                    'description': description

                }
            ))

    def take_order_departure_city_messaged(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="take_order_departure_city_messaged",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))
    def take_order_make_mistake_departure_city(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="Take_order_make_mistake_departure_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def take_order_corected_by_list_departure_city(self, user_id, time, button_type):
        self.client.track(
            BaseEvent(
                event_type="Take_order_corected_by_list_departure_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'type_of_button': button_type
                }
            ))


    def take_order_departure_city_correction_messaged(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="take_order_departure_city_correction_messaged",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))


    def take_order_destination_city_messaged(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="take_order_destination_city_messaged",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def take_order_make_mistake_destanation_city(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="Take_order_make_mistake_destanation_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def take_order_corected_by_list_destenation_city(self, user_id, time, button_type):
        self.client.track(
            BaseEvent(
                event_type="Take_order_corected_by_list_destenation_city",
                user_id=user_id,
                time=time,
                event_properties={
                    'type_of_button': button_type
                }
            ))

    def take_order_destination_city_correction_messaged(self, user_id, time, text):
        self.client.track(
            BaseEvent(
                event_type="take_order_destination_city_correction_messaged",
                user_id=user_id,
                time=time,
                event_properties={
                    'text': text
                }
            ))

    def take_order_route_confermed(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="Take_order_route_confermed",
                user_id=user_id,
                time=time
            ))

    def take_order_order_taken(self, user_id, time, order_id, costumer):
        self.client.track(
            BaseEvent(
                event_type="Take_order_order_taken",
                user_id=user_id,
                time=time,
                event_properties={
                    'order_id': order_id,
                    'costumer': costumer


                }
            ))

    def take_order_user_flow_finished(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="Take_order_user_flow_finished",
                user_id=user_id,
                time=time
            ))

    def watching_statisics_finished_orders_shown(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="Watching_statisics_finished_orders_shown",
                user_id=user_id,
                time=time
            ))

    def watching_statisics_inprogress_orders_shown(self, user_id, time):
        self.client.track(
            BaseEvent(
                event_type="Watching_statisics_inprogress_orders_shown ",
                user_id=user_id,
                time=time
            ))
