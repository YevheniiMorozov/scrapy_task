from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from crud import session, get_all_apartments
import serializing

api = FastAPI()


@api.get('/')
async def get_results(
        location: Optional[str] = None,
        dt: Optional[str] = None,
        price: Optional[str] = None,
        hydro: Optional[bool] = None,
        heat: Optional[bool] = None,
        water: Optional[bool] = None,
        wifi: Optional[bool] = None,
        pet_friendly: Optional[bool] = None,
        parking: Optional[int] = None,
        dishwasher: Optional[bool] = None,
        fridge: Optional[bool] = None,
        air_condition: Optional[bool] = None,
        outdoor_space: Optional[bool] = None,
        smocking_permitted: Optional[bool] = None,
):
    if dt:
        dt = [serializing.time_serializer(value) for value in dt.split("-")]
        # dt = [value for value in dt.split("/")]
    if price:
        price = [int(pr) for pr in price.split("-")]
    filters = {
        "location":
            {
                "name": location
             },
        'utilities': {
            "hydro": hydro,
            "heat": heat,
            "water": water,
            "wifi": wifi,
            'pet_friendly': pet_friendly,
            "parking": parking,
            },
        "unit": {
            "dishwasher": dishwasher,
            "fridge": fridge,
            "air_condition": air_condition,
            "outdoor_space": outdoor_space,
            'smocking_permitted': smocking_permitted
            }
        }

    apartments_list = await get_all_apartments(session, filters=filters, price=price, dt=dt)
    results = {'apartments':
        [
            {
                "id": el.apartment_id,
                "title": el.title,
                "location_id": el.location_id,
                "address": el.address,
                'published': el.published,
                "price": el.price,
                "user_id": el.id,
                'include_utilities': el.include_utilities,
                'utilities_id': el.utilities_id,
                "unit_id": el.unit_id,
                "description": el.description,
                "location": el.location.name,
                "utilities": {
                    "hydro": el.utilities.hydro,
                    "heat": el.utilities.heat,
                    "water": el.utilities.water,
                    "wifi": el.utilities.wifi,
                    "parking": el.utilities.parking,
                    "agreement": el.utilities.agreement,
                    "move_in_date": el.utilities.move_in_date,
                    "pet_friendly": el.utilities.pet_friendly,
                },
                "unit": {
                    "size": el.unit.size,
                    "furnished": el.unit.furnished,
                    "laundry": el.unit.laundry,
                    'dishwasher': el.unit.dishwasher,
                    'fridge': el.unit.fridge,
                    "air_condition": el.unit.air_condition,
                    "outdoor_space": el.unit.outdoor_space,
                    "smoking_permitted": el.unit.smocking_permitted
                },
                "user": {
                    "profile": el.user.profile,
                    "owner": el.user.owner,
                    "listing": el.user.listing,
                    "registry_time": el.user.registry_time,
                    'website': el.user.website
                }
            }
            for el in apartments_list
        ]
    }
    return JSONResponse(content=jsonable_encoder(results))
