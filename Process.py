from Limit import *
from ProcessCall import *


class Process(Limit):
    def __init__(self, newnames, messages, processcalls, subprocesses):
        Limit.__init__(self, newnames, messages, processcalls, subprocesses, [], [])

    def get_fixedpart(self):
        return self

    def is_proc(self):
        return True

    def make_limit_from_proc(self):
        return Limit(self.newnames, self.messages, self.processcalls, self.subprocesses, [], [])


class StopProcess(Process):
    def __init__(self):
        Process.__init__(self, set(), [], [], [])

    def __str__(self):
        return 'STOP'

    def str_tex(self):
        return '\\textbf{0}'

    def rename_name_repr(self, repr_man):
        return self

    def is_stopproc(self):
        return True

    def rename(self, theta):
        return self

    def substitute_variables(self, substitutions):
        return self
