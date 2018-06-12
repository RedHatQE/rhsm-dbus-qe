#!/bin/bash
#pipenv run py.test -s --color=yes --count=1000 --verbose src/test_status_signal.py
#pipenv run py.test -s --color=yes --verbose src/test_status_signal.py
pipenv run py.test -s --color=yes --verbose src/suites/dbus-config-testsuite.py
