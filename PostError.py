# PostError.py

from collections import defaultdict


class PostError:

    def __init__(self, proccall, continuation, limit, left, right, substitution = None, intruder_names = None,
                 name_repr_man = None):
        self.init_proccall = proccall
        # self.matched_message = matched_message
        self.substitution_used = substitution
        self.continuation = continuation
        self.invariant_to_check = limit
        # Eventually share the invariant between different errors maybe
        self.left_side = left
        self.right_side = right
        self.name_repr_man = name_repr_man
        self.intruder_names = intruder_names

    def __str__(self):
        # matched message can stay None if tau
        return 'Process Call ' + str(self.init_proccall) + '\n' + \
               'has the following continuation ' + str(self.continuation) + '\n' + \
               'which does not seem to be included in this invariant: \n' + str(self.invariant_to_check) + '\n' + \
               'More verbose: \n \t Left \t' + str(self.left_side) + '\n' + \
               ' \t Right \t' + str(self.right_side) + '\n'

    def set_name_repr_man(self, name_repr_man):
        self.name_repr_man = name_repr_man

    # def set_matched_message(self, msg):
    #     self.matched_message = msg

    def set_substitution_used(self, subst):
        self.substitution_used = subst

    def set_intruder_names(self, intruder_names):
        self.intruder_names = intruder_names

    # Eventually, do the back-translation of an error here but for now still in NameReprManager
    def rename(self, substitution):
        init_proccall = self.init_proccall.rename(substitution)
        if self.substitution_used is not None:
            substitution_matching = dict({})
            for (k, v) in self.substitution_used.iteritems():
                substitution_matching[substitution.get(k, k)] = v.rename(substitution)
        else:
            substitution_matching = None
        continutation = self.continuation.rename(substitution)
        invariant_to_check = self.invariant_to_check.rename(substitution)
        left_side = self.left_side.rename(substitution)
        right_side = self.right_side.rename(substitution)
        # intruder_names cannot be renamed (yet) due to uniqueness
        return PostError(init_proccall, continutation, invariant_to_check, left_side, right_side, substitution_matching,
                         self.intruder_names, self.name_repr_man)

    def get_str_repr_of_substitution(self):
        representation = str()
        if self.substitution_used is None:
            representation += 'tau-transition'
        else:
            for (k, v) in self.substitution_used.iteritems():
                representation += str(k) + ' -> ' + str(v) + ';  '
        return representation

