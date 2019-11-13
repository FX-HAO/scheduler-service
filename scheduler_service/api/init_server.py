import databases


async def setup_databases(app, loop):
    app._databases = databases.Database(app.config['MODEL_URL'])


async def close_databases(app, loop):
    await app._databases.disconnect()
