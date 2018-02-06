import asyncio
import aiohttp
from PyRP import rp
import json
import addict
import xmltodict
import datetime

config = addict.Dict(json.load(open('config.json')))
loop = asyncio.ProactorEventLoop()

rpc = rp.DiscordRPC(str(config.discord.client_id), loop, False)
ip = config.vlc.ip

async def get_data():
    auth = aiohttp.BasicAuth('', config.vlc.password)
    async with aiohttp.ClientSession(auth=auth) as cs:
        async with cs.get(f'http://{ip}/requests/status.xml') as r:
            text = await r.read()
            return text.decode('utf-8')

class Track:
    def __init__(self, filename, artist=None, album=None, title=None, length:int=None, now:int=None, state=None):
        self.filename = filename
        self.artist = artist
        self.album = album
        self.title = title
        self.length = length
        self.state = state
        self.now = now

async def send_rp_data(trk):
    payload = addict.Dict({
        "details": "",
        "assets": {
            'large_text': 'VLC Media Player',
            'large_image': 'cone'
        },
    })

    filename = trk.filename
    title = trk.title
    name = title or filename
    current = trk.length - trk.now
    playing = (trk.state == 'playing')
    album = trk.album

    payload.details = f"{'' if not trk.artist else f'{trk.artist} - '}{name}"
    payload.state = album if album else ('Playing' if playing else 'Paused')

    await rpc.send_rich_presence(payload.to_dict())

def parse(thing):
    a = ['album', 'filename', 'date', 'artist']
    b = addict.Dict()
    for i in thing:
        i = addict.Dict(i)
        try:
            awau = a.index(i['@name'])
            b[a[awau]] = i['#text']
        except Exception:
            continue
    return b


async def run():
    print('''
VLC Media Player - Rich Presence for Discord
(c) ry00001 2018
This software is closed-source (for the time being, anyways.)
Starting up...
    ''')
    await rpc.start()
    while True:
        try:
            data = await get_data()
            data = addict.Dict(xmltodict.parse(data)).root
            thing = parse(data.information.category[0].info)
            filename = thing.filename
            artist = thing.artist
            date = thing.date
            album = thing.album
            total = int(data.length)
            now = int(data.time)
            state = data.state
            track = Track(filename, now=now, length=total, state=state, artist=artist, album=album)
            await send_rp_data(track)
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            print('Shutting down...')
            exit()

loop.run_until_complete(run())
