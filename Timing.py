from Process import *
from parser.InputParser import get_program_from_file_input
import time


def time_widening_sampling(filename, c=2, expected=True):
    if c == 0:
        raise Exception('Cannot sample 0 times')
    time_sum = 0
    for _ in range(c):
        time_sum += time_widening_once(filename, expected)
    return time_sum / c


def time_widening_once(filename, expected):
    ProcessCall.definitions = dict()
    program = get_program_from_file_input(filename)
    start = time.time()
    program.widen_initial_configuration()
    end = time.time()
    assert (program.is_an_invariant() == expected)
    return end - start


def time_inv_check_sampling(filename, c=2):
    if c == 0:
        raise Exception('Cannot sample 0 times')
    time_sum = 0
    for _ in range(c):
        time_sum += time_inv_check_once(filename)
    return time_sum / c


def time_inv_check_once(filename):
    ProcessCall.definitions = dict()
    program = get_program_from_file_input(filename)
    program.rename_name_repr()
    start = time.time()
    assert program.is_an_invariant()
    end = time.time()
    return end - start
