async def setup_database(app, loop):
    await app._database.connect()


async def close_database(app, loop):
    await app._databases.disconnect()


async def close_motor(app, loop):
    app.mclient.close()
