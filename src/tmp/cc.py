import websockets, os
from colorama import Fore
from urllib.parse import urljoin
import logging, asyncio, logging.config, json

from rx import Observable
from rx.subjects import Subject

configStream = Subject()
logging.config.fileConfig("logging.conf")

configStream.subscribe(lambda x: print('message arrived'))

async def consume(prefix, baseurl, path):
    async with websockets.connect(urljoin(baseurl,path)) as ws:
        async for msg in ws:
            logging.info(prefix + path + " a message arrived")
            configStream.on_next({ws: ws, path: path, msg: msg})

consumers = [
    consume(Fore.RED + "01 " + Fore.RESET, os.getenv('RHSM_SERVICES_URL'),'/monitor/etc/rhsm/rhsm.conf'),
    consume(Fore.GREEN + "02 " + Fore.RESET, os.getenv('RHSM_SERVICES_URL'),'/monitor/etc/rhsm/rhsm.conf'),
    consume(Fore.BLUE + "03 " + Fore.RESET, os.getenv('RHSM_SERVICES_URL'),'/monitor/etc/rhsm/rhsm.conf'),
]

async def waitForConsumers(consumers):
    for res in asyncio.as_completed(consumers):
        await res

asyncio.get_event_loop().run_until_complete(waitForConsumers(consumers))
