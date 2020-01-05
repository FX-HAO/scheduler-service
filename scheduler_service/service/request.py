from aiohttp import ClientSession
from bson import ObjectId

from scheduler_service import mongo_db


async def ping(ctx, oid):
    session: ClientSession = ctx['session']
    task = await mongo_db.task.find({'_id': ObjectId(oid)})
    for url in task.urls:
        async with session.get(url.request_url, params=url.params) as resp:
            await resp.text()
