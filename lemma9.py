import argparse

import os
import sys

from parser.InputParser import get_program_from_file_input
from Program import *

parser = argparse.ArgumentParser(prog='lemma9',
                                 usage='%(prog)s [-h] path (-c | -i #iterations)',
                                 description='With this small CLI, '
                                             'one can check inductivity of a model '
                                             'or obtain a (partial) invariant from a model '
                                             '(with initial configuration) indicating the number of iterations to try.',
                                 epilog='For example models, please refer to the `benchmark` folder.')

# Add the arguments

parser.add_argument('path_model',
                    metavar='path',
                    type=str,
                    help='the path to the model')

option = parser.add_mutually_exclusive_group(required=True)
option.add_argument('-c', '--check', action='store_true', dest='check')
option.add_argument('-i', '--infer', action='store', type=int, choices=range(1, 20), dest='num_iterations')

# parse the command line content
args = parser.parse_args()

input_path = args.path_model

# Check if the model exists
if not os.path.isfile(input_path):
    print 'The model specified does not exist.'
    sys.exit()

program = get_program_from_file_input(input_path)

# If it exists, do what is ought to be done

# check candidate invariant
if args.check:
    program.rename_name_repr()
    print 'Checking whether the provided model is an invariant... \n'
    if program.is_an_invariant():
        print 'It is an invariant: \n'
        # program.pretty_definitions()
        program.prettyprint_invariant()
    else:
        print '\nIt is not an invariant. The following errors have not been resolved: \n'
        print program.get_string_repr_errors()
        print 'Please, consider integrating (at least) one of them and run the tool with the inference option.\n'
    sys.exit()
# infer invariant
else:
    print 'Inferring a candidate invariant... \n'
    result = program.widen_initial_configuration(counter=args.num_iterations)
    print 'The following candidate invariant has been obtained. (We omit the definitions given in the model.) \n'
    result.prettyprint_invariant()
    if program.is_an_invariant():
        print '\nIt is an invariant! \n'
    else:
        print '\nIt is not an invariant. The following errors have not been resolved: \n'
        print result.get_string_repr_errors()
        print 'Please, consider integrating (at least) one of them and run the inference again.\n'
    sys.exit()


