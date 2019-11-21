async def setup_database(app, loop):
    await app._database.connect()


async def close_database(app, loop):
    await app._databases.disconnect()
