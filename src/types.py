from collections import namedtuple
from typing import (NamedTuple, Any)

class IOTuple(NamedTuple):
    ws: Any
    path: str
    msg: str

#IOTuple = namedtuple('IOTuple',['ws','path','msg'])

Scenario = namedtuple('Scenario',['scenario','scenario_id','events'])
Verification = namedtuple('Verification',['status','msg'])
Result = namedtuple('Result',['status','msg','verifications'])

TestRun = namedtuple('TestRun',  ['short_desc','scenario','result'])
TestSuite = namedtuple('TestSuite',['short_desc','testsuite_id','testruns','result'])

