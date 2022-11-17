from sqlalchemy import Column, Integer, String, create_engine, Boolean, DateTime, ForeignKey
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import relationship
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from apartments.apartments import settings

Base = declarative_base()


def db_connect() -> Engine:
    return create_engine(URL(**settings.DATABASE))


def create_items_table(engine: Engine):
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    profile = Column(String(250), unique=True)
    owner = Column(Boolean)
    listing = Column(Integer)
    registry_time = Column(String(50))
    website = Column(String(50))


class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)


class Utilities(Base):
    __tablename__ = 'utilities'
    id = Column(Integer, primary_key=True)
    hydro = Column(Boolean)
    heat = Column(Boolean)
    water = Column(Boolean)
    wifi = Column(Boolean)
    parking = Column(Integer)
    agreement = Column(String(50))
    move_in_date = Column(DateTime)
    pet_friendly = Column(Boolean)


class Unit(Base):
    __tablename__ = 'unit'

    id = Column(Integer, primary_key=True)
    size = Column(Integer, nullable=True)
    furnished = Column(Boolean)
    laundry = Column(Boolean)
    dishwasher = Column(Boolean)
    fridge = Column(Boolean)
    air_condition = Column(Boolean)
    outdoor_space = Column(Boolean)
    smocking_permitted = Column(Boolean)


class Apartments(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    location_id = Column(ForeignKey(Location.id))
    location = relationship(Location)
    apartment_id = Column(Integer, unique=True, nullable=False)
    address = Column(String(200))
    published = Column(DateTime)
    price = Column(String(500), nullabule=True)
    user_id = Column(ForeignKey(User.id))
    user = relationship(User)
    utilities_id = Column(ForeignKey(Utilities.id))
    included_utilities = relationship(Utilities)
    unit_id = Column(ForeignKey(Unit.id))
    unit = relationship(Unit)
    description = Column(String(500))