import os, multiprocessing, asyncio, websockets

from colorama import Fore
from threading import current_thread
from urllib.parse import urljoin

from rx import Observable
from rx.concurrency import ThreadPoolScheduler
from rx.subjects import Subject

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

configStream01 = Subject()
configStream02 = Subject()

async def joinWith(ws,configStream):
    print("join with")
    async for message in ws:
        configStream.on_next(message)

async def main():
    url = urljoin(os.getenv('RHSM_SERVICES_URL'),'/monitor/etc/rhsm/rhsm.conf');
    print(url)
    for stream in [configStream01,configStream02]:
        print ('next stream')
        await joinWith(await websockets.connect(url), stream)

    configStream01.subscribe_on(pool_scheduler).subscribe(lambda x: print(Fore.RED + '01 - {0}'.format(x)))
    configStream02.subscribe_on(pool_scheduler).subscribe(lambda x: print(Fore.GREEN + '01 - {0}'.format(x)))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
