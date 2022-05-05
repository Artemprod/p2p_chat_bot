from db.db_connectors import DBOffersManager, OfferFilter
from db.tables import OfferInDB
from secrets import SECRETS
import datetime as dt


def main():
    print(f"SECRETS = {SECRETS}")
    manager = DBOffersManager(
        user=SECRETS.bd_user,
        password=SECRETS.bd_password,
        host=SECRETS.bd_host,
        port=SECRETS.bd_port,
        database=SECRETS.database
    )
    try:
        filters = OfferFilter(
            departure_city="departure_city",
            destination_country="destination_country"
        )
        offer: OfferInDB = manager.add_offer(OfferInDB(
            customer_user_id=1,
            created_date=dt.datetime.utcnow(),
            price=1.123,
            description="description",
            status="status",
            dispatch_date=dt.datetime.utcnow(),
            departure_city=filters.departure_city,
            destination_country=filters.destination_country
        ))
        found_offer: OfferInDB = manager.find_one_offer(filters=filters)
        assert found_offer.departure_city == filters.departure_city
        assert found_offer.destination_country == filters.destination_country

        not_found_offer = manager.find_one_offer(filters=OfferFilter(
            departure_city="123",
            destination_country="321"
        ))
        assert not_found_offer is None
    finally:
        manager.close()


if __name__ == "__main__":
    main()
