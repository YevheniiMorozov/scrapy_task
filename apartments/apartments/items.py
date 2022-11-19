# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from apartments.apartments.serializing_and_ua import time_serializer


class User:
    pass


class LocationItem:
    location = scrapy.Field()


class UnitItem:
    size = scrapy.Item(serializer=int)
    furnished = scrapy.Field(serializer=bool)
    laundry = scrapy.Field(serializer=bool)
    dishwasher = scrapy.Field(serializer=bool)
    fridge = scrapy.Field(serializer=bool)
    air_condition = scrapy.Field(serializer=bool)
    outdoor_space = scrapy.Field(serializer=bool)
    smocking_permitted = scrapy.Field(serializer=bool)


class UtilitiesItem:
    hydro = scrapy.Field(serializer=bool)
    heat = scrapy.Field(serializer=bool)
    water = scrapy.Field(serializer=bool)
    wifi = scrapy.Field(serializer=bool)
    parking = scrapy.Item(serializer=int)
    agreement = scrapy.Item(serializer=str)
    move_in_date = scrapy.Item(serializer=str)
    pet_friendly = scrapy.Field(serializer=bool)


class UserItem():
    pass


class ApartmentsItem(scrapy.Item):
    title = scrapy.Item(serializer=str)
    location = LocationItem()
    apartment_id = scrapy.Item(serializer=int)
    address = scrapy.Item(serializer=str)
    published = scrapy.Item(serializer=time_serializer)
    price = scrapy.Item(serializer=str)
    user = UserItem()
    included_utilities = UtilitiesItem()
    unit = UnitItem
    description = scrapy.Item(serializer=str)
