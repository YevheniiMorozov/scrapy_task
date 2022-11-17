# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from models import Apartments, User, Utilities, Unit, Location, create_items_table, db_connect


class ApartmentsPipeline:

    def __init__(self):
        engine = db_connect()
        create_items_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        instance = session.query(Location).filter_by(**item['location']).one_or_none()
        if instance:
            return instance
        location_instance = Location(**item)
        instance = session.query(Unit).filter_by(**item['location']).one_or_none()
        if instance:
            return instance
        unit_instance = Unit(**item)

