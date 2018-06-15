from funcy import complement
from .types import TestRun, Result, Scenario
from colorama import Fore

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
        return acc + (ioTuple.msg,)

    return stream.take_while(complement(end_of_scenario(scenario,scenario_id)))\
        .reduce(reducer,())\
        .map(lambda events: Scenario(scenario,scenario_id,events))


def report_log_str_for_testsuite(ts):
    return "\n".join()
    pass

def writeToFile(fname):
    def handler(data):
        with open(fname,"wt") as ws:
            ws.write(json.dumps(data))
        pass
    return handler

