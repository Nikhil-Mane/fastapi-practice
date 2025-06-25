"""HTTP client utility for AsyncJobQueue."""
import aiohttp

async def call_external_api(url, payload):
    """Call an external API with the given URL and payload."""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json() 