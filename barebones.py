import asyncio
from PyRP import rp
loop = asyncio.ProactorEventLoop()
rpc = rp.DiscordRPC('410531021818429449', loop, False) # replace that ID with your RP app's client ID

async def run():
    await rpc.start() # call this before anything else!
    while True:
        await rpc.send_rich_presence({
            'details': "Isn't PyRP neat?",
            'state': "Rich presence in Python!"
        })
        await asyncio.sleep(1)

loop.run_until_complete(run())
