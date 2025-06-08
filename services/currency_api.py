import asyncio
import aiohttp
from config.settings import CURRENCY_API_KEY

import aiohttp
from config.settings import CURRENCY_API_KEY


async def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    if not CURRENCY_API_KEY:
        return None

    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if data.get("result") == "success":
                    return data["conversion_result"]
                return None
    except Exception as e:
        print(f"API error: {e}")
        return None