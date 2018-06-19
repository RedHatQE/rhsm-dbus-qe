import websockets, os
from colorama import Fore
from urllib.parse import urljoin
import logging, asyncio, logging.config, json

# irc.devel.redhat.com 6667
# irc.lab.bos.redhat.com 6667
# irc-2.devel.redhat.com
# irc.yyz.redhat.com
# irc.eng.brq.redhat.com 6667


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
    lambda : print('end of the show')
)
subscriptionManagerStream.subscribe(
    printMessage('subscription manager message arrived\t'),
    lambda err: print(err),
    lambda : print('end of the show')
)

entitlementUnknownStatusStream = entitlementStatusStream\
    .distinct_until_changed(lambda x: x['msg']['overallStatus'])\
    .filter(lambda x: x['msg']['overallStatus'] == 'Unknown')

entitlementUnknownStatusStream\
    .subscribe(printMessage('entitlement status is unknown\t'))

async def consume(baseurl, path, stream):
    async with websockets.connect(urljoin(baseurl,path)) as ws:
        async for msg in ws:
            stream.on_next({'ws': ws, 'path': path, 'msg': json.loads(msg)})

#start a scenarion
async def runRegistration():
    [x,y] = await Observable.zip(entitlementUnknownStatusStream, subscriptionManagerStream, lambda x,y: [x,y]).take(1)
    print('about to send a registration')
    await y['ws'].send('register --username testuser1 --password password --org admin')
    status = await entitlementStatusStream

#
# lada chrnik autoservis pro fordy: 776 13 73 22
#

coroutines = [
    consume(os.getenv('RHSM_SERVICES_URL'),'/rhsm/status',entitlementStatusStream),
    consume(os.getenv('RHSM_SERVICES_URL'),'/execute/usr/bin/subscription-manager',subscriptionManagerStream),
    runRegistration()
]

async def waitForCoroutines(coroutines):
    for res in asyncio.as_completed(coroutines):
        await res

loop = asyncio.get_event_loop()
loop.run_until_complete(waitForCoroutines(coroutines))
asyncio.close()
