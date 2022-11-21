from sqlalchemy import Column, Integer, String,  Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    profile = Column(String(250), unique=True)
    owner = Column(Boolean)
    listing = Column(Integer, nullable=True)
    registry_time = Column(String(50))
    website = Column(String(50), nullable=True)


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
    move_in_date = Column(DateTime, nullable=True)
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
    price = Column(Integer, nullable=True)
    user_id = Column(ForeignKey(User.id))
    user = relationship(User)
    include_utilities = Column(String(50))
    utilities_id = Column(ForeignKey(Utilities.id))
    utilities = relationship(Utilities)
    unit_id = Column(ForeignKey(Unit.id))
    unit = relationship(Unit)
    description = Column(String(2500))


if __name__ == '__main__':
    from .db_settings import db_connect
    Base.metadata.drop_all(db_connect())
    Base.metadata.create_all(db_connect())
