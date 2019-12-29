from motor import motor_asyncio


async def setup_database(app, loop):
    await app._database.connect()


async def close_database(app, loop):
    await app._databases.disconnect()


async def setup_motor(app, loop):
    app.mongo_client = motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017", io_loop=loop)
    app.mongo_db = app.mongo_client['test']


async def close_motor(app, loop):
    app.mclient.close()
