# Integration/Functional Tests for RHSM DBus Service
## Overview
This package provides a pile of tests for RHSM DBus Service.
The service is a base communication layer for `subscription-manager`. 

`subscription-manager` is a tool that user entitles RedHat's content by.

The tests uses `Python3.6` and `RxPy`. The code is base on `Reactive Programming` approach. You can read more about [Reactive Programming](http://reactivex.io)

The tests use a message broker [RHSM Services](https://github.com/RedHatQE/rhsm-services). It is a server that provides `websocket` services needed by real-time test analysis
and `REST` based services for synchronous test operations. The main purpose of this broker is providing of real-time informations about a tested system.

## Desing of the Testing Process

It is necessary to understand a way how this testing game is written before you run the tests.

There are three main players in this testing game:
- user scenario - a shell script or ansible script
- message broker `RHSM Service` - a central piece of the game
- a test - an observer that takes signals from the message broker and analyzes them 

*A testing process is driven by user scenarion* Shortly - a test does not run any action in a tested system. 
It does not change a system state at all. It just receives signals from the system and analyzes them.

   
## Requirements
The base requirement is 
  - `Python3.6` or later
  - [Pipenv](https://github.com/pypa/pipenv)
  
## Installation

```shell
# install python3.6 and pipenv
cd ~/src/rhsm-dbus-qd
pipenv install
```

## Running

The proper tests start once you run the right user scenario.

## What is the benefit of reactive approach for testing?

You know, the most expensive task is to prepare a tested system into the right state.

You know how a system is prepared in 'before suite' method of a testware and all tests in the test suite rely upon the state of the system the 'before suite' method prepared.
But if some test change a system state (ie. calls some system action - `subscription-manager register`) the state has been changed. You can see a lot of `subscription-manager register/unregister` 
commands in the tests.

Supposing you want to test everything about a DBus objects `com.redhat.RHSM1.Config` and `com.redhat.RHSM1.Product`. First test should test that an interface exists in a command result `busctl tree`.

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

With this approach a command `busctl tree` was run twice. You know, system actions are expensive.

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
   
In this approach a system action `busctl tree` was run just once and it's result was used by two tests.

### Summary
In reactive way:
- a test just listen for the right messages
- a test is waken up once the right script is run
- testing game is just about a flow of data - it is a sort of data mining
- a testing game is split into independent design tasks:
   - write user scenario
   - send informations from the system into testware
   - let testware shake it's way and analyze the informations
   
