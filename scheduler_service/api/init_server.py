async def close_databases(app, loop):
    await app._databases.disconnect()
