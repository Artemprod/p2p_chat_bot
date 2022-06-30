import datetime as dt
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects import postgresql as sql_pg
from sqlmodel import Field, SQLModel


class Offers(SQLModel, table=True):
    id: int = Field(
        default=None,
        description="Package id",
        sa_column=Column(
            "id",
            sql_pg.INTEGER,
            autoincrement=True,
            primary_key=True,
            index=False,
            nullable=False,
        ),
    )
    customer_user_id: int
    type: Optional[str]
    created_date: dt.datetime
    departure_country: Optional[str]
    departure_city: Optional[str]
    destination_country: Optional[str]
    destination_city: Optional[str]
    price: float
    description: str
    title: Optional[str]
    status: str
    dispatch_date: dt.datetime

    @property
    def package_id(self) -> int:
        return self.id

    @property
    def despatch_date(self) -> dt.datetime:
        return self.dispatch_date

    @property
    def custumer_user_id(self) -> int:
        return self.customer_user_id


OfferInDB = Offers

offers_filter_create = """
-- Table: public.offers_filtr

-- DROP TABLE IF EXISTS public.offers_filtr;

CREATE TABLE IF NOT EXISTS public.offers_filtr
(
    user_id integer NOT NULL,
    departure_country character varying COLLATE pg_catalog."default",
    departure_city character varying COLLATE pg_catalog."default",
    destination_country character varying COLLATE pg_catalog."default",
    destination_city character varying COLLATE pg_catalog."default",
    price numeric
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.offers_filtr
    OWNER to postgres;
"""

users_create = """
-- Table: public.users

-- DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    "UserName" character varying(100) COLLATE pg_catalog."default" NOT NULL,
    "UserNickName" character varying(100) COLLATE pg_catalog."default" NOT NULL,
    "Email" character varying(100) COLLATE pg_catalog."default",
    "PhoneNumber" character varying(100) COLLATE pg_catalog."default",
    "UserLastName" character varying(100) COLLATE pg_catalog."default",
    user_id integer NOT NULL,
    telegram_name character varying COLLATE pg_catalog."default",
    "Link" character varying COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.users
    OWNER to postgres;
"""

# TODO: chat_id + user_id -> Unique
user_chat_create = """
-- Table: public.user_chat

-- DROP TABLE IF EXISTS public.user_chat;

CREATE TABLE IF NOT EXISTS public.user_chat
(
    chat_id integer,
    user_id integer,
    "ChatStatus" integer,
    "LastAnswer " text COLLATE pg_catalog."default",
     previous_status character varying COLLATE pg_catalog."default",
     first_lounch date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.user_chat
    OWNER to postgres;
"""

# TODO: package_id + user_id -> Unique
shown_offers_create = """
-- Table: public.shown_offers

-- DROP TABLE IF EXISTS public.shown_offers;

CREATE TABLE IF NOT EXISTS public.shown_offers
(
    user_id integer,
    package_id integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.shown_offers
    OWNER to postgres;
"""

packages_create = """
-- Table: public.packages

-- DROP TABLE IF EXISTS public.packages;

CREATE TABLE IF NOT EXISTS public.packages
(
    package_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    custumer_user_id integer NOT NULL,
    type character varying(100) COLLATE pg_catalog."default",
    created_date date,
    departure_country character varying(255) COLLATE pg_catalog."default",
    departure_city character varying(255) COLLATE pg_catalog."default",
    destination_country character varying(255) COLLATE pg_catalog."default",
    destination_city character varying(255) COLLATE pg_catalog."default",
    price numeric,
    description text COLLATE pg_catalog."default",
    title character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    despatch_date date,
    package_size character varying COLLATE pg_catalog."default",
    CONSTRAINT packages_pkey PRIMARY KEY (package_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.packages
    OWNER to postgres;

COMMENT ON TABLE public.packages
    IS 'all created packages from all users ';
"""

# TODO: costumer_id + executor_id + package_id -> unique
# TODO: order_id -> unique
# TODO: исправить опечатки в названия колонок и потом в коде соответственно
orders_create = """
-- Table: public.orders

-- DROP TABLE IF EXISTS public.orders;

CREATE TABLE IF NOT EXISTS public.orders
(
    costumer_id integer NOT NULL,
    executor_id integer NOT NULL,
    order_start_date date,
    order_finish_date date,
    package_id integer NOT NULL,
    order_chat_id integer,
    unique_order_numner bigint,
    status character varying COLLATE pg_catalog."default",
    order_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 )
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.orders
    OWNER to postgres;

COMMENT ON TABLE public.orders
    IS 'table defines  work proces ';
"""

CREATE_SCRIPTS = (
    offers_filter_create, users_create, user_chat_create,
    shown_offers_create, packages_create, orders_create
)
