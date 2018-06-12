import websockets, os
from colorama import Fore
from urllib.parse import urljoin
import logging, asyncio, logging.config, json
import pytest
from datetime import datetime

from rx import Observable
from rx.subjects import Subject

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

# notifies all stream how testing goes on
testingStatusStream = Subject()

entitlementStatusStream = Subject()
subscriptionManagerStream = Subject()
entitlementStatusesDuringTest = entitlementStatusStream\
                                .take_until(testingStatusStream.filter(lambda x: x == 'testing finished').take(1)) \
                                .reduce(lambda acc,x: acc + [x['msg']],[])

async def consume(baseurl, path, stream):
    async with websockets.connect(urljoin(baseurl,path)) as ws:
        async for msg in ws:
            #print('new msg arrived')
            #print(json.loads(msg))
            stream.on_next({'ws': ws, 'path': path, 'msg': json.loads(msg)})

@pytest.yield_fixture()
def event_loop():
    loop = asyncio.get_event_loop()

    consumers = [
        asyncio.ensure_future(consume(os.getenv('RHSM_SERVICES_URL'),'/ws/rhsm/status',entitlementStatusStream)),
        asyncio.ensure_future(consume(os.getenv('RHSM_SERVICES_URL'),'/ws/execute/usr/bin/subscription-manager',subscriptionManagerStream)),
        asyncio.ensure_future(entitlementStatusesDuringTest),
    ]
    loop.consumers = consumers
    yield loop
    for consumer in consumers:
        consumer.cancel()

async def test_status_signal(event_loop):
    testingStatusStream.on_next("testing started")
    sm = await subscriptionManagerStream.take(1)
    await sm['ws'].send('identity')
    # waiting for response
    sm = await subscriptionManagerStream.take(1)

    await sm['ws'].send('unregister')
    sm = await subscriptionManagerStream.take(1)

    await sm['ws'].send('register --username testuser1 --password password --org admin')
    sm = await subscriptionManagerStream.take(1)

    testingStatusStream.on_next("testing finished")
    statusEvents = await event_loop.consumers[2]
    assert len(statusEvents) >= 2
    lastTwoStatusEvents = statusEvents[-2:]
    assert [ii['overallStatus'] for ii in lastTwoStatusEvents] == ['Unknown','Invalid']

async def test_status_signal_02(event_loop):
    testingStatusStream.on_next("testing started")
    sm = await subscriptionManagerStream.take(1)
    await sm['ws'].send('identity')
    # waiting for response
    sm = await subscriptionManagerStream.take(1)

    await sm['ws'].send('unregister')
    sm = await subscriptionManagerStream.take(1)

    await sm['ws'].send('register --username testuser1 --password password --org admin')
    sm = await subscriptionManagerStream.take(1)

    testingStatusStream.on_next("testing finished")
    statusEvents = await event_loop.consumers[2]
    assert len(statusEvents) >= 2
    lastTwoStatusEvents = statusEvents[-2:]
    assert [ii['overallStatus'] for ii in lastTwoStatusEvents] == ['Unknown','Invalid']
