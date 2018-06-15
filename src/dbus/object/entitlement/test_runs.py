from functools import reduce
from rx.subjects import Subject
from src.tools import (start_of_scenario,
                       reduce_scenario)
from src.types import (TestRun,Result)
from src.streams import streams

from src.dbus.verifications import verify_dbus_object_exists

rx_test_entitlement_object_exists = streams['/ws/testware/monitor'] \
    .filter(start_of_scenario('busctl-tree.sh')) \
    .flat_map(lambda ioTuple: reduce_scenario(
                                              ioTuple.msg['scenario'],
                                              ioTuple.msg['scenario_id'],
                                              streams['/ws/testware/monitor']))\
    .map(lambda scenario: [scenario, [verify_dbus_object_exists("/com/redhat/RHSM1/Entitlement")(scenario.events)]])\
    .map(lambda x: TestRun("Entitlement object exists in DBus system tree",
                           scenario = x[0],
                           result = Result(status = reduce(lambda acc,x: acc and x, [v.status for v in x[1]]),
                                           msg = "",
                                           verifications = x[1])))
