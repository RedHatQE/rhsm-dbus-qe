from src.types import (Verification, TestRun, TestSuite)
from functools import singledispatch
from colorama import Fore

def colored_status(status):
    return "{0}{1}{2}".format(status and Fore.GREEN or Fore.RED,
                              status,
                              Fore.RESET)
def colored_short_status(status):
    return "{0}{1}{2}".format(status and Fore.GREEN or Fore.RED,
                              status and 'T' or 'F',
                              Fore.RESET)

@singledispatch
def short_log_str(x):
    """ This method provides a short str reprezentation of an object.
    The string reprezentation is used for short reporting how a testing goes on"""
    return "the method short_log_str is used for printing a results"


@short_log_str.register(Verification)
def report_log_str_for_verification(verification):
    return "{0} - {1}".format(colored_short_status(verification.status),verification.msg)

@short_log_str.register(TestRun)
def _ (tr):
    return "\n".join(["{0} - {1}".format(colored_status(tr.result.status),tr.short_desc),
    ] + (tr.result.msg and ["\t" + tr.result.msg] or []) +\
                     ["\t" + short_log_str(v) for v in tr.result.verifications])

@short_log_str.register(TestSuite)
def _ (ts):
    return "\n".join(["{0} - {1} ({2})".format(colored_status(ts.result.status),
                                               ts.short_desc,
                                               ts.testsuite_id or '-'),
                      "\t" + "".join([colored_short_status(tr.result.status) for tr in ts.testruns])])
