# Integration/Functional Tests for RHSM DBus Service
## Overview
This package provides a pile of tests for RHSM DBus Service.
The service is a base communication layer for `subscription-manager`. 

`subscription-manager` is a tool that user entitles RedHat's content by.

The tests uses `Python3.6` and `RxPy`. The code is based on [Reactive Programming](http://reactivex.io).

The tests use a message broker [RHSM Services](https://github.com/RedHatQE/rhsm-services). It is a server that provides `websocket` services needed by real-time test analysis
and `REST` based services for synchronous test operations. The main purpose of this broker is providing of real-time informations about a tested system.

## Desing of a Testing Process

It is necessary to understand a way how this testing game is written before you run the tests.

There are three main players in this testing game:
- **user scenario** - a shell script or ansible script
- **message broker** `RHSM Service` - a central piece of the game
- **a test** - an observer that takes signals from the message broker and analyzes them 

> A testing process is driven by user scenarion. Shortly - a test does not run any action in a tested system. 
> It does not change a system state at all. It just receives signals from the system and analyzes them.


   
## Requirements
The base requirement is 
  - `Python3.6` or later
  - [Pipenv](https://github.com/pypa/pipenv)

> An important part of the testing game is `RHSM-services` message broker. 
> It is necessary to install in on a tested machine. see [RHSM Services Git Repo](https://github.com/RedHatQE/rhsm-services)

## Installation

```shell
# install python3.6 and pipenv
cd ~/src/rhsm-dbus-qe
pipenv install
```

> It is necessary to set `.env` file in the root directory. You can see an example of the file in the directory.
> The file contains of properties used by the testware.

## Running

The proper tests start once you run the right user scenario.

1. run the testware

```shell
# run Tier1 Test Suite
cd ~/src/rhsm-dbus-qe
pipenv run python3.6 src/suite/tier1.py
```

2. run a user scenario
```shell
ssh root@centos7.example.com
/opt/rhsm-services/resources/scenario/dbus/busctl-tree.sh
```

> Testware runs forever listening incomming signals. The only thing you have to run again and again is the right scenario.

## Main Parts of this Repo
|                              |                        |
|------------------------------|------------------------|
| user scenarion               | `./resouces/scenarion` |
| dbus tests                   | `./src/dbus`           |
| data types                   | `./src/types.py`       |
| streams used in the testware | `./src/streams.py`     |
| test suites                  | `./src/suite`          |

## What is the Benefit of Reactive Approach for Testing?

> Reactive programming offers an easy way to data mine. It offers a pile of methods to transform,merge,aggregate streams of events.

You know - the most expensive task is to prepare a tested system into the right state.

You know how a system is prepared in `before suite` method of a testware and all tests 
in the test suite rely upon the state of the system the 'before suite' method prepared.
But if some test change a system state (ie. calls some system action - `subscription-manager register`) 
the state has been changed. You can see a lot of `subscription-manager register/unregister` 
commands in the tests.

Supposing you want to test everything about a DBus objects `com.redhat.RHSM1.Config` and `com.redhat.RHSM1.Product`.
Tests should verify that an interface exists in a command result `busctl tree`.

The traditional test looks like this:

1. test

```shell
run a command `busctl tree`
parse the response
verify that 'com.redhat.RHSM1.Config' exists in the response
be happy when the interface exists
```
2. test

```shell
run a command `busctl tree`
parse the response
verify that 'com.redhat.RHSM1.Product' exists in the response
be happy when the interface exists
```

The command `busctl tree` was run twice using the traditional approach.

The reactive approach looks like this:

1. run a command busctl and send all informations to a testware

```shell
send a message 'hey, busctl-tree is in the air!' into testware
run a command `busctl tree`
send a response of the command into testware
send a message 'it was pleasure to run the script - see you soon!'
```

2. let testware listen for the right messages
3. when a message 'hey, busctl-tree is in the air!' appears
   those two tests awake and start collecting the messages
4. once the script stops emitting messages the two tests analyze the messages.
   You know, there is a message 'response of busctl tree command'
   
The command `busctl tree` was run just once using the reactive approach and a result of the command was used by two tests.

> You know - system actions are expensive!

### Summary
In reactive way:
- a test just listen for the right messages
- a test is waken up once the right script is run
- testing game is just about a flow of data - it is a sort of data mining
- a testing game is split into independent design tasks:
   - to write user scenario
   - to send informations from the system into testware
   - let testware shake it's way and analyze the informations
- this approach offers a new way to cooperate - reporters often send a bug 
  with a short shell based scenario to reproduce a bug.
  A tester can reuse the shell scenario and it is necessary to extend it by signals emitting only.
- two people can work together on one test 
   - the first one can write user scenario and signals emitting
   - the second one can write test analysis
