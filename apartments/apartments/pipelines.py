# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from .models import Apartments, User, Utilities, Unit, Location
from .db_settings import db_connect, create_items_table


class ApartmentsPipeline:

    def __init__(self):
        self.engine = db_connect()
        create_items_table(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def process_item(self, item, spider):
        print(item['apartment']['apartment_id'])
        with self.Session() as session:
            if session.query(Apartments).filter_by(**item['apartment']).first():
                raise DropItem("Duplicate item")
            units = Unit(**item['units'])
            utilities = Utilities(**item['utilities'])
            apartment = Apartments(**item["apartment"])
            apartment.utilities = utilities
            apartment.unit = units
            location = session.query(Location).filter_by(**item['location']).first()
            location_id = location.id if location else None
            if not location:
                location = Location(**item["location"])
                print("Commit location ", location.name)
                session.add(location)
                session.commit()
                location = session.query(Location).filter_by(**item['location']).first()
                location_id = location.id if location else None
                apartment.location_id = location_id
            else:
                apartment.location_id = location_id
            user = session.query(User).filter_by(**item['user']).first()
            user_id = user.id if user else None
            if not user:
                user = User(**item["user"])
                apartment.user = user
            else:
                apartment.user_id = user_id
            session.add(utilities)
            session.commit()
            session.add(units)
            session.commit()
            session.add(user)
            session.commit()
            session.add(apartment)
            session.commit()
