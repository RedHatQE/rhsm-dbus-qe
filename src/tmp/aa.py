from colorama import Fore
import asyncio
import multiprocessing
from threading import current_thread
from rx import Observable
from rx.concurrency import ThreadPoolScheduler

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

numbers01 = Observable.from_(range(10)).subscribe_on(pool_scheduler)
numbers02 = Observable.from_(range(10)).subscribe_on(pool_scheduler)

async def main():
    numbers01.subscribe(lambda x: print(Fore.RED + '01 - {0}'.format(x)))
    numbers02.subscribe(lambda x: print(Fore.GREEN + '02 - {0}'.format(x)))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
