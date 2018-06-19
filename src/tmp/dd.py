import websockets, os
from colorama import Fore
from urllib.parse import urljoin
import logging, asyncio, logging.config, json

#
# 600Kc mamce
#

from rx import Observable
from rx.subjects import Subject
logging.config.fileConfig("logging.conf")

def printMessage(prefix):
    def handler(x):
        ws,path,msg = [x.get(key) for key in ['ws','path','msg']]
        print(prefix,msg);
    return handler

entitlementStatusStream = Subject()
subscriptionManagerStream = Subject()

entitlementStatusStream.subscribe(
    printMessage('entitlement status arrived \t'),
    lambda err: print(err),
    lambda x: print('end of the show')
)
subscriptionManagerStream.subscribe(
    printMessage('subscription manager message arrived\t'),
    lambda err: print(err),
    lambda x: print('end of the show')
)
entitlementStatusStream\
    .distinct_until_changed(lambda x: x['msg']['overallStatus'])\
    .filter(lambda x: x['msg']['overallStatus'] == 'Unknown')\
    .subscribe(printMessage('entitlement status is unknown\t'))

entitlementStatusStream.zip(subscriptionManagerStream)\
    .subscribe(
        lambda x: print(x),
        lambda err: print(err),
        lambda x: print("konec")
    )

async def consume(baseurl, path, stream):
    async with websockets.connect(urljoin(baseurl,path)) as ws:
        async for msg in ws:
            stream.on_next({'ws': ws, 'path': path, 'msg': json.loads(msg)})


consumers = [
    consume(os.getenv('RHSM_SERVICES_URL'),'/rhsm/status', entitlementStatusStream),
    consume(os.getenv('RHSM_SERVICES_URL'),'/rhsm/status', entitlementStatusStream),
    consume(os.getenv('RHSM_SERVICES_URL'),'/rhsm/status', entitlementStatusStream),
    consume(os.getenv('RHSM_SERVICES_URL'),'/execute/usr/bin/subscription-manager', subscriptionManagerStream)
]

async def waitForConsumers(consumers):
    for res in asyncio.as_completed(consumers):
        await res

# #start a scenarion
# Observable.zip(entitlementStatusStream,subscriptionManagerStream)\
#           .take(1)\
#           .subscribe(lambda x: print(x))

asyncio.get_event_loop().run_until_complete(waitForConsumers(consumers))
