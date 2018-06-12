import websockets, os
from colorama import Fore
from urllib.parse import urljoin
import logging, asyncio, logging.config, json
from datetime import datetime
from collections import namedtuple
from funcy import complement

from rx import Observable
from rx.subjects import Subject

streams = {
    "/ws/rhsm/config": Subject(),
    "/ws/testware/monitor": Subject(),
    "/ws/dbus/system/monitor": Subject(),
}

IOTuple = namedtuple('IOTuple',['ws','path','msg'])
ScenarioEvent = namedtuple('ScenarioEvent',['type','scenario','scenario_id','time','msg'])
TestRun = namedtuple('TestRun',  ['scenario','scenario_id','events'])
TestSuite = namedtuple('TestSuite',['testsuite','testsuite_id','testruns'])
TestRunResult = namedtuple('TestRunResult',[])
TestSuiteResult = namedtuple('TestSuiteResult',[])

def start_of_scenario(scenario):
    def handler(ioTuple):
        return ioTuple.msg.get('scenario') == scenario \
            and ioTuple.msg.get('type') == "start of scenario"
    return handler

def end_of_scenario(scenario, scenario_id):
    def handler(ioTuple):
        isEnd = ioTuple.msg.get('scenario') == scenario \
            and ioTuple.msg.get('scenario_id') == scenario_id \
            and ioTuple.msg.get('type') == 'end of scenario'
        return isEnd
    return handler

def reduce_scenario(scenario, scenario_id, stream):
    def reducer(acc, ioTuple):
        #print("{0},{1}".format(acc.scenario,acc.scenario_id))
        return TestRun(acc.scenario, acc.scenario_id, acc.events + (ioTuple.msg,))

    return stream.take_while(complement(end_of_scenario(scenario,scenario_id)))\
        .reduce(reducer,TestRun(scenario,scenario_id,()))

def writeToFile(fname):
    def handler(data):
        with open(fname,"wt") as ws:
            ws.write(json.dumps(data))
        pass
    return handler

rx_test_config_object_exists = streams['/ws/testware/monitor'] \
    .filter(start_of_scenario('busctl-tree.sh')) \
    .flat_map(lambda ioTuple: reduce_scenario(ioTuple.msg['scenario'],
                                              ioTuple.msg['scenario_id'],
                                              streams['/ws/testware/monitor']))

rx_test_config_object_exists.subscribe(writeToFile("test-config-object-exists.json"))

async def feed(path, stream):
    async with websockets.connect(urljoin(os.getenv('RHSM_SERVICES_URL'),path)) as ws:
        async for msg in ws:
            stream.on_next(IOTuple(ws,path,json.loads(msg)))

def run(loop):
    consumers = [
        feed('/ws/rhsm/config',streams['/ws/rhsm/config']),
        feed('/ws/testware/monitor',streams['/ws/testware/monitor']),
        feed('/ws/dbus/system/monitor',streams['/ws/dbus/system/monitor']),
    ]
    loop.run_until_complete(asyncio.gather(*consumers))


run(asyncio.get_event_loop())
