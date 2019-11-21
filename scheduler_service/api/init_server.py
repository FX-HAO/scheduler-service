async def setup_database(app, loop):
    await app._dtabase.connect()


async def close_database(app, loop):
    await app._databases.disconnect()
