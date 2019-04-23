from Message import *


class Variable:
    def __init__(self, name, size=0):
        self.name = name
        self.sized = False
        self.size = 0
        if size != 0:
            self.size = size
            self.sized = True

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        # does not check for size!
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def __str__(self):
        if self.sized:
            return '(' + str(self.name) + ' : size ' + str(self.size) + ')'
        else:
            return str(self.name)

    def str_tex(self):
        if len(self.name) > 1:
            return self.name[0] + '_{' + self.name[1:] + '}'
        return str(self.name)

    def get_variables(self):
        return set([self])

    def get_names(self):
        return set()

    def get_kind(self):
        return KindMsg.VAR

    def is_message(self):
        return False

    def substitute_variables(self, substitutions):
        return substitutions.get(self, self)

    def rename(self, theta):
        return self

    def get_msg_to_match(self):
        return self

    def is_two_ary_msg(self):
        return False


def numbers_of_new_names(set_vars):
    ret = 0
    for v in set_vars:
        if not v.sized:
            raise Exception('Variable to fill without size')
        assert v.sized
        ret += 2 ** (v.size - 1)
    return ret


def variables(*args):
    setofvars = set()
    for v in args:
        assert isinstance(v, str)
        setofvars.add(Variable(v))
    return setofvars
