# secrets_leaks.py

from Action import Action
from Definition import Definition
from ProcessCall import ProcessCall
from InputPrefix import InputPrefix
from Variable import Variable
from Process import Process


def get_secret_action(continuation):
    return Action(InputPrefix({}, Variable('x')), continuation)


def get_leak_action(continuation):
    return Action(InputPrefix(None, None), continuation)


def get_secret_proccall():
    return ProcessCall('Secret', Variable('x'))


def get_leak_proccall():
    return ProcessCall('Leak', Variable('x'))


def get_leak_proc():
    return Process(set(), [], [get_leak_proccall()], [])


def get_secret_definition():
    secret_proccall = get_secret_proccall()
    return Definition(secret_proccall, [get_secret_action(get_leak_proc())])


def get_leak_definition():
    leak_proccall = get_leak_proccall()
    return Definition(leak_proccall, [get_leak_action(get_leak_proc())])

