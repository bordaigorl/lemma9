from Message import KindMsg
from Variable import numbers_of_new_names, Variable
from KnowledgeHandler import reduce_knowledge, get_pairs_from_list_of_msgs
from InclusionCheck import check_inclusion_of_continuation
from copy import deepcopy
from Message import BasicMsg
from InputPrefix import InputPrefix
from PostError import *
from Process import StopProcess


class Action:
    def __init__(self, inputprefix, continuation):
        # Check whether a variable is simply forwarded (and no other information is gained from this)
        # i.e. no pattern match like v, {v}_k or a continuation -'[..., v, ...] s.t. the called pc could do sth else
        # while the first is harder to capture, the second could be determined by a causality chain with annotations
        # but cycles are permitted there
        if inputprefix.tau:
            self.inputprefix = inputprefix
            self.continuation = continuation
        else:
            continuation_copy = deepcopy(continuation)
            continuation_copy.normalise()
            continuation_copy.reduce_knowledge()
            # Maybe only unwrapping pairs is more desirable
            pattern_to_red = [inputprefix.msg]
            reduce_knowledge(pattern_to_red)
            variables_to_remove = set()
            for v in inputprefix.variables:
                if v in continuation_copy.messages and v in pattern_to_red:
                    # check whether it is used somewhere else
                    continuation_copy.messages.remove(v) # need to delete to check but add if not ow.
                    if v not in continuation_copy.get_variables():
                        # now check whether it occurs only once in the input pattern
                        removed_v_in_pattern = filter(lambda x: v is not x, pattern_to_red)
                        # subst_pattern = map(lambda x: x.substitute_variables(substitution_to_check), removed_v_in_pattern)
                        if len(filter(lambda x: v in x.get_variables(), removed_v_in_pattern)) == 0:
                            pattern_to_red = removed_v_in_pattern
                            variables_to_remove.add(v)
                    else:
                        continuation.messages.append(v)
            if len(variables_to_remove) is 0:
                self.inputprefix = inputprefix
            else:
                new_set_of_vars = inputprefix.variables - variables_to_remove
                if len(new_set_of_vars) is 0:
                    self.inputprefix = InputPrefix(None, None)
                else:
                    new_pattern = get_pairs_from_list_of_msgs(pattern_to_red)
                    self.inputprefix = InputPrefix(new_set_of_vars, new_pattern)
            if continuation_copy.is_empty():
                self.continuation = StopProcess()
            else:
                self.continuation = continuation_copy

    # Only for test cases
    @staticmethod
    def get_action_wo_fwd_check(inputprefix, continuation):
        orginal_tau = inputprefix.tau
        inputprefix.tau = True
        action = Action(inputprefix, continuation)
        action.inputprefix.tau = orginal_tau
        return action

    def __str__(self):
        return str(self.inputprefix) + '(' + str(self.continuation) + ')'

    def str_tex(self):
        return self.inputprefix.str_tex() + '(' + self.continuation.str_tex() + ')'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def get_freenames(self):
        return self.continuation.get_globalnames() - self.get_variables()

    def get_boundnames(self):
        return self.continuation.get_all_boundnames()

    def get_variables(self):
        return self.inputprefix.get_variables()

    def take_step(self, message):
        eligible, substitution = self.inputprefix.input_message(message)
        if eligible:
            names_in_substitutions = set()
            for v in substitution.itervalues():
                names_in_substitutions.update(v.get_names())
            if names_in_substitutions & self.continuation.newnames:
                raise Exception('Substitutions contain newnames from continuation')
            return self.continuation.substitute_variables(substitution)
        else:
            return None  # raise Exception not eligible

    def substitute_variables(self, substitution, knowledge = []):
        return Action(self.inputprefix.substitute_variables(substitution),
                      self.continuation.substitute_variables(substitution))

    def is_prefixtau(self):
        return self.inputprefix.tau

    def get_extension_factor_and_annotation(self, messages):
        if self.is_prefixtau() | self.continuation.is_empty():
            return 1, None
        annotation = self.inputprefix.annotate_inputpattern(messages)
        if not annotation.get_value():
            return 0, annotation
        vars_to_be_filled = self.inputprefix.compute_variables_to_be_filled(annotation)
        number_new_names = numbers_of_new_names(vars_to_be_filled)
        return max(number_new_names, 1), annotation

    def check_every_post_for_inclusion(self, proccall, annotation, limit, intruder_names):
        # Switch on for sanity check which process calls were fired
        # print proccall
        list_of_errors = []
        if self.is_prefixtau():
            current_error = check_inclusion_of_continuation(limit, deepcopy(self.continuation), proccall, False)
            if current_error is not None:
                current_error.set_intruder_names(set())
                list_of_errors.append(current_error)
        elif self.continuation.is_empty():
            return []
        else:
            messages = limit.messages + [BasicMsg(i) for i in intruder_names]
            substitutions = self.inputprefix.get_substitutions_from_annotation_and_knowledge(annotation, messages)
            # Use annotation to compute the different possible substitutions -> substitutions
            for substitution in substitutions:
                continuation = self.continuation.substitute_variables(substitution)
                used_intruder_names = intruder_names & (continuation.get_globalnames())
                continuation.newnames.update(used_intruder_names)
                continuation.messages.extend([BasicMsg(i) for i in used_intruder_names])
                # Omitted deepcopy here as substitute_variables returns copy anyway
                intruders_used = len(intruder_names) > 0
                current_error = check_inclusion_of_continuation(limit, continuation, proccall, intruders_used)
                if current_error is not None:
                    current_error.set_intruder_names(intruder_names)
                    # Compute message from substitution:
                    # matched_message = self.inputprefix.msg.substitute_variables(substitution)
                    # current_error.set_matched_message(matched_message)
                    current_error.set_substitution_used(substitution)
                    list_of_errors.append(current_error)
        return list_of_errors

    def rename_name_repr(self, repr_man):
        # Action does not have global names by definition
        self.continuation = self.continuation.rename_name_repr(repr_man)

    def rename(self, substitution):
        return Action(deepcopy(self.inputprefix), self.continuation.rename(substitution))

