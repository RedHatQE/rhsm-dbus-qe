import websockets, os
from urllib.parse import urljoin
import logging, asyncio, logging.config, json
from datetime import datetime
from funcy import (all, complement)
import re
from rx import Observable
from collections import namedtuple

from src.tools import (end_of_scenario,
                       start_of_scenario,
                       reduce_scenario)
from src.types import (IOTuple,
                       Verification,
                       Result,
                       TestRun,
                       TestSuite)

from src.streams import streams
from src.dbus.object.config.test_runs import (
    rx_test_config_object_exists,
)
from src.dbus.object.entitlement.test_runs import (
    rx_test_entitlement_object_exists,
)
from src.dbus.object.product.test_runs import (
    rx_test_product_object_exists,
)
from src.dbus.object.SubscriptionManager.test_runs import (
    rx_test_subscriptionManager_object_exists,
    rx_test_entitlement_status_changed_appears,
)

from src.dbus.object.Customer.test_runs import (
    rx_test_customer_object_exists,
    rx_test_customer_changed_appears,
)

IndexedTestRun = namedtuple('IndexedTestRun',['index','testrun'])

from src.short_log_strs import (short_log_str)

# -------- partial test reports - for each test itself
rx_test_config_object_exists.scan(lambda acc,tr: IndexedTestRun(acc.index + 1, tr),
                                  IndexedTestRun(0,None))\
                            .subscribe(lambda itr: print(str(itr.index) + " " + short_log_str(itr.testrun)))

rx_test_entitlement_object_exists.scan(lambda acc,tr: IndexedTestRun(acc.index + 1, tr),
                                       IndexedTestRun(0,None))\
                                 .subscribe(lambda itr: print(str(itr.index) + " " + short_log_str(itr.testrun)))

rx_test_product_object_exists.scan(lambda acc,tr: IndexedTestRun(acc.index + 1, tr),
                                   IndexedTestRun(0,None))\
                             .subscribe(lambda itr: print(str(itr.index) + " " + short_log_str(itr.testrun)))

rx_test_subscriptionManager_object_exists.scan(lambda acc,tr: IndexedTestRun(acc.index + 1, tr),
                                               IndexedTestRun(0,None))\
                                         .subscribe(lambda itr: print(str(itr.index) + " " + short_log_str(itr.testrun)))

rx_test_entitlement_status_changed_appears.scan(lambda acc,tr: IndexedTestRun(acc.index + 1, tr),
                                                IndexedTestRun(0,None))\
                                          .subscribe(lambda itr: print(str(itr.index) + " " + short_log_str(itr.testrun)))

rx_test_customer_object_exists.scan(lambda acc,tr: IndexedTestRun(acc.index + 1, tr),
                                    IndexedTestRun(0,None))\
                              .subscribe(lambda itr: print(str(itr.index) + " " + short_log_str(itr.testrun)))

rx_test_customer_changed_appears.scan(lambda acc,tr: IndexedTestRun(acc.index + 1, tr),
                                                IndexedTestRun(0,None))\
                                          .subscribe(lambda itr: print(str(itr.index) + " " + short_log_str(itr.testrun)))

# ------ overall test suite report - for the whole test suite
rx_test_config_object_exists.zip(rx_test_entitlement_object_exists,
                                 rx_test_product_object_exists,
                                 rx_test_subscriptionManager_object_exists,
                                 rx_test_entitlement_status_changed_appears,
                                 rx_test_customer_object_exists,
                                 rx_test_customer_changed_appears,
                                 lambda *args: list(args))\
                            .map(lambda trs: [trs, all(lambda tr: tr.result.status == True, trs)])\
                            .map(lambda x: TestSuite(short_desc = "Tier1 RHSM DBus Test Suite",
                                                     testsuite_id = None,
                                                     testruns = x[0],
                                                     result = Result(status = x[1],
                                                                     msg = "",
                                                                     verifications = [ Verification(status=x[1],msg="")])))\
                            .subscribe(lambda ts: print("------------------------------\n" + short_log_str(ts)))

#rx_test_config_object_exists.subscribe(print)
#rx_test_config_object_exists.subscribe(writeToFile("test-config-object-exists.json"))

# --- feeding of reactive testware by testware events
async def feed(path, stream):
    async with websockets.connect(urljoin(os.getenv('RHSM_SERVICES_URL'),path)) as ws:
        async for msg in ws:
            # a reactive stream starts shaking
            stream.on_next(IOTuple(ws,path,json.loads(msg)))

def run(loop):
    consumers = [feed(url,streams[url]) for url in streams.keys()]
    loop.run_until_complete(asyncio.gather(*consumers))

run(asyncio.get_event_loop())
