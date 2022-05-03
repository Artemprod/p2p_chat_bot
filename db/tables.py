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
