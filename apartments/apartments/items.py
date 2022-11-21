# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from .serializing import time_serializer


class LocationItem(scrapy.Item):
    name = scrapy.Field()


class UnitItem(scrapy.Item):
    size = scrapy.Field(serializer=int)
    furnished = scrapy.Field(serializer=bool)
    laundry = scrapy.Field(serializer=bool)
    dishwasher = scrapy.Field(serializer=bool)
    fridge = scrapy.Field(serializer=bool)
    air_condition = scrapy.Field(serializer=bool)
    outdoor_space = scrapy.Field(serializer=bool)
    smocking_permitted = scrapy.Field(serializer=bool)


class UtilitiesItem(scrapy.Item):
    hydro = scrapy.Field(serializer=bool)
    heat = scrapy.Field(serializer=bool)
    water = scrapy.Field(serializer=bool)
    wifi = scrapy.Field(serializer=bool)
    parking = scrapy.Field(serializer=int)
    agreement = scrapy.Field(serializer=str)
    move_in_date = scrapy.Field(serializer=time_serializer)
    pet_friendly = scrapy.Field(serializer=bool)


class UserItem(scrapy.Item):
    profile = scrapy.Field()
    owner = scrapy.Field(serializer=bool)
    registry_time = scrapy.Field()
    listing = scrapy.Field(serializer=int)
    website = scrapy.Field()


class ApartmentsItem(scrapy.Item):
    title = scrapy.Field(serializer=str)
    apartment_id = scrapy.Field(serializer=int)
    address = scrapy.Field(serializer=str)
    published = scrapy.Field(serializer=time_serializer)
    price = scrapy.Field(serializer=int)
    include_utilities = scrapy.Field(serializer=str)
    description = scrapy.Field(serializer=str)
