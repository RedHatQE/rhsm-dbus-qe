from functools import reduce
from rx.subjects import Subject
from src.tools import (start_of_scenario,
                       reduce_scenario)
from src.types import (TestRun,Result)
from src.streams import streams

from src.dbus.verifications import (
    verify_dbus_object_exists,
    verify_dbus_signal_was_emitted
)

rx_test_subscriptionManager_object_exists = streams['/ws/testware/monitor'] \
    .filter(start_of_scenario('busctl-tree.sh')) \
    .flat_map(lambda ioTuple: reduce_scenario(ioTuple.msg['scenario'],
                                              ioTuple.msg['scenario_id'],
                                              streams['/ws/testware/monitor']))\
    .map(lambda scenario: [scenario, [verify_dbus_object_exists('/com/redhat/RHSM1/SubscriptionManager')\
                                      (scenario.events)]])\
    .map(lambda x: TestRun("SubscriptionManager object exists in DBus system tree",
                           scenario = x[0],
                           result = Result(status = reduce(lambda acc,x: acc and x, [v.status for v in x[1]]),
                                           msg = "",
                                           verifications = x[1])))

rx_test_entitlement_status_changed_appears = streams['/ws/testware/monitor'] \
    .filter(start_of_scenario('unregister-register.sh')) \
    .flat_map(lambda ioTuple: reduce_scenario(ioTuple.msg['scenario'],
                                              ioTuple.msg['scenario_id'],
                                              streams['/ws/testware/monitor']\
                                              .merge(streams['/ws/dbus/system/monitor'])))\
    .map(lambda scenario: [scenario, [verify_dbus_signal_was_emitted(path='/EntitlementStatus',
                                                                     interface='com.redhat.SubscriptionManager.EntitlementStatus',
                                                                     member='entitlement_status_changed')\
                                      (scenario.events)]])\
    .map(lambda x: TestRun("EntitlementStatus/entitlement_status_changed is emitted once I register a system",
                           scenario = x[0],
                           result = Result(status = reduce(lambda acc,x: acc and x, [v.status for v in x[1]]),
                                           msg = "",
                                           verifications = x[1])))
