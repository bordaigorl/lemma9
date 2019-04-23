from NameReprManager import NameReprManager
from Definition import Definition
from Process import Process
from InclusionCheck import check_inclusion
from secrets_leaks import get_secret_definition, get_leak_definition, get_leak_proc
from Widening import widen_iteratively


class Program(object):

    def __init__(self, definitions, limit, helpers=None):
        self.definitions = definitions
        secret_def = get_secret_definition()
        self.definitions.append(secret_def)
        leak_def = get_leak_definition()
        self.definitions.append(leak_def)
        self.helpers = helpers
        self.limit = limit
        self.name_repr_man = None
        self.error_list = None

    def __str__(self):
        definitions_repr = '\n'.join(str(d) for d in self.definitions)
        return definitions_repr + '\n' + str(self.limit)

    def prettyprint_with_ids(self):
        substitution = self.name_repr_man.get_substitution_with_ids()
        pretty_limit = self.limit.rename(substitution)
        print pretty_limit

    def prettyprint_invariant(self):
        substitution = self.name_repr_man.get_substitution_without_ids()
        pretty_limit = self.limit.rename(substitution)
        print pretty_limit.print_with_helper_defs()

    def pretty_definitions(self):
        substitution = self.name_repr_man.get_substitution_without_ids()
        definitions = [d.rename(substitution) for d in self.definitions]
        return definitions

    def pretty_invariant_tex(self):
        substitution = self.name_repr_man.get_substitution_without_ids()
        pretty_limit = self.limit.rename(substitution)
        return pretty_limit.print_with_helper_defs_tex()

    def pretty_program_tex(self):
        # definitions
        representation = '\\[ \n\\begin{array}{lcl} \n'
        for d in self.pretty_definitions():
            representation += d.str_tex() + '; \\\\ \n'
        representation += '\\end{array} \\]\n'
        # invariant with helper definitions
        representation += self.pretty_invariant_tex() + '\n'
        return representation

    def pretty_error_list(self):
        if self.error_list is None:
            self.error_list = self.limit.get_pretty_error_list_of_posts(self.name_repr_man)
        return self.get_string_repr_errors()

    def get_string_repr_errors(self):
        assert self.error_list is not None
        str_repr = str()
        for error in self.error_list:
            str_repr = str_repr + str(error) + '\n'
        return str_repr

    def rename_local_names(self):
        map(lambda definition: definition.rename_name_repr(self.name_repr_man), self.definitions)
        self.limit = self.limit.rename_name_repr(self.name_repr_man)

    def rename_global_names(self):
        global_names = self.limit.get_globalnames()
        theta = self.name_repr_man.get_substitution_for_set(global_names)
        self.limit = self.limit.rename(theta)
        # by definition no global names in definitions
        # self.definitions = map(lambda definition: definition.rename(theta), self.definitions)

    def rename_name_repr(self):
        self.name_repr_man = NameReprManager()
        self.rename_global_names()
        self.rename_local_names()

    def is_an_invariant(self):
        if self.error_list is None:
            self.error_list = self.limit.get_pretty_error_list_of_posts(self.name_repr_man)
        if self.error_list:
            return False
        else:
            return True

    def check_secrecy(self):
        self.error_list = None # Flush error list
        secret_def = get_secret_definition()
        self.definitions.append(secret_def)
        leak_def = get_leak_definition()
        self.definitions.append(leak_def)
        if self.is_an_invariant():
            if check_inclusion(get_leak_proc(), self.limit):
                return 'Leak in invariant'# Leak in invariant
            else:
                return 'Secret not leaked'
        else:
            return 'Not an invariant' # Not an invariant

    def compute_error_list_for_invariant(self):
        self.error_list = self.limit.get_pretty_error_list_of_posts(self.name_repr_man)

    def widen_initial_configuration(self, counter = 15):
        no_errors_left, program = widen_iteratively(self, counter)
        return program
