from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import models as md
import settings


settings.DATABASE["drivername"] = 'postgresql+asyncpg'
engine = create_async_engine(URL.create(**settings.DATABASE))
session = AsyncSession(engine)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(md.Base.metadata.create_all)


async def get_all_apartments(session: AsyncSession, filters: dict = None, price: list = None, dt: list = None):
    location = await session.execute(select(md.Location).filter_by(**filters["location"]).limit(1))
    location = location.scalars().first()
    location_id = location.id
    result = await session.execute(select(md.Apartments)
                                   .options(selectinload(md.Apartments.location))
                                   .filter(md.Apartments.location_id == location_id)
                                   .options(selectinload(md.Apartments.utilities))
                                   .options(selectinload(md.Apartments.unit))
                                   .options(selectinload(md.Apartments.user))
                                   .order_by(md.Apartments.published.desc()).limit(200))
    if dt:
        dt_from, dt_to = dt
        result = await session.execute(select(md.Apartments)
                                       .filter(md.Apartments.published.between(dt_from, dt_to),
                                               md.Apartments.location_id == location_id)
                                       .options(selectinload(md.Apartments.location))
                                       .options(selectinload(md.Apartments.utilities))
                                       .options(selectinload(md.Apartments.unit))
                                       .options(selectinload(md.Apartments.user))
                                       .order_by(md.Apartments.published.desc()).limit(200))
    if price:
        price_from, price_to = price
        result = await session.execute(select(md.Apartments)
                                       .filter(md.Apartments.price.between(price_from, price_to))
                                       .options(selectinload(md.Apartments.location))
                                       .options(selectinload(md.Apartments.utilities))
                                       .options(selectinload(md.Apartments.unit))
                                       .options(selectinload(md.Apartments.user))
                                       .order_by(md.Apartments.published.desc()).limit(200))

    return result.scalars().all()





