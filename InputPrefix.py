from Message import *
from collections import defaultdict
from Variable import *
from KnowledgeHandler import constructable_from, all_messages_of_size
from SubstitutionHandler import combine_lists_of_substitutions, get_substitution, get_eligible_substitutions, check_for_eligible_message
from Annotation import *


class InputPrefix:

    def __init__(self, variables, msg):
        if (variables is None) & (msg is None):
            self.tau = True
            self.variables = set()
            self.msg = None
        else:
            self.tau = False
            if not variables <= msg.get_variables():
                # print str(variables) + '\n'
                # print str(msg)
                raise Exception('Not enough variables in pattern of action')
            if isinstance(variables, Variable):
                variables = set([variables])
            self.variables = variables
            # update pattern in a way such that information about size of variables is in pattern
            newmsg = msg.substitute_variables(dict([(v, v) for v in variables]))
            self.msg = newmsg

    def __str__(self):
        if self.tau:
            return "tau."
        else:
            if len(self.variables) == 0:
                return 'in(' + self.msg.str_tex() + ').'
            repnames = ", ". join(str(x) for x in self.variables)
            return 'in(' + repnames + ' : ' + str(self.msg) + ').'

    def str_tex(self):
        if self.tau:
            return "\\tau."
        else:
            if len(self.variables) == 0:
                return '\\inp{' + self.msg.str_tex() + '}.'
            repnames = ", ". join(x.str_tex() for x in self.variables)
            return '\\inp{' + repnames + ' : ' + self.msg.str_tex() + '}.'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def get_variables(self):
        if self.tau:
            return set()
        else:
            return self.variables

    def input_message(self, message):
        msg_to_match = self.msg.get_msg_to_match()
        return get_substitution(msg_to_match, message)

    def substitute_variables(self, substitution):
        if self.tau:
            return self
        else:
            return InputPrefix(self.variables, self.msg.substitute_variables(substitution))

    def annotate_inputpattern(self, messages):
        msg_to_match = self.msg.get_msg_to_match()
        to_visit = [(True, msg_to_match)]
        results = []
        while to_visit:
            m, pat = to_visit.pop()
            if m:
                if pat.is_two_ary_msg():
                    to_visit.append((False, pat))
                    to_visit.append((True, pat.second))
                    to_visit.append((True, pat.first))
                elif pat.get_kind() == KindMsg.VAR:
                    results.append(BscAnnotation(KindSubs.CONSTR))
                elif pat.is_message():
                    if constructable_from(pat, messages):
                        results.append(BscAnnotation(KindSubs.CONSTR))
                    else:
                        results.append(BscAnnotation(KindSubs.BOTTOM))
                else:
                    raise Exception("BasicMsg should be a message")
            else:
                if pat.is_two_ary_msg():
                    right = results.pop()
                    left = results.pop()
                    if left.get_bool() & right.get_bool():
                        results.append(StrAnnotation(KindSubs.CONSTR, left, right))
                    # Check for eligible messages if encry
                    elif ((pat.get_kind() == KindMsg.ENC) | (pat.get_kind() == KindMsg.AENC) | (pat.get_kind() == KindMsg.SIGN)) \
                            & check_for_eligible_message(pat, messages):
                            results.append(StrAnnotation(KindSubs.ELIGIBLE, left, right))
                    else:
                        results.append(StrAnnotation(KindSubs.BOTTOM, left, right))
                    # In the last two cases, one could actually omit the sub-annotations as they will never be use
                elif pat.get_kind() == KindMsg.PUB:
                    private_res = results.pop()
                    if private_res.get_bool():
                        results.append(StrAnnotation(KindSubs.CONSTR, private_res, None)) # private key leaked
                    elif check_for_eligible_message(pat, messages):
                        results.append(StrAnnotation(KindSubs.ELIGIBLE, private_res, None))
                    else:
                        results.append(StrAnnotation(KindSubs.BOTTOM, private_res, None))
        assert len(results) == 1
        return results[0]

    def compute_variables_to_be_filled(self, annotation):
        msg_to_match = self.msg.get_msg_to_match()
        to_visit = [(msg_to_match, annotation)]
        variables_to_be_filled = set()
        variables_determined = set()
        while to_visit:
            node, annotation = to_visit.pop()
            mode = annotation.get_value()
            if mode == KindSubs.ELIGIBLE:
                variables_determined.update(node.get_variables())
                # Add all variables to the set
            elif mode == KindSubs.CONSTR:
                if node.get_kind() == KindMsg.VAR:
                    variables_to_be_filled.add(node)
                elif node.is_two_ary_msg():
                    comps = node.get_comps()
                    to_visit.append((comps[1], annotation.right))
                    to_visit.append((comps[0], annotation.left))
            else:
                raise Exception('We should never reach BOTTOM here.')
        return variables_to_be_filled - variables_determined

    def get_substitutions_from_annotation_and_knowledge(self, annotation, messages):
        # Use annotation to compute the variables which are determined by substitutions s.t. they are not generated
        if not annotation.get_value():
            return []
        vars_to_be_filled = self.compute_variables_to_be_filled(annotation)
        msg_to_match = self.msg.get_msg_to_match()
        to_visit = [(True, annotation, msg_to_match)]
        results = []
        while to_visit:
            m, anno, pat = to_visit.pop()
            if m:
                if anno.get_value() == KindSubs.ELIGIBLE:
                    # get all substitutions from knowledge and push to results
                    results.append(get_eligible_substitutions(pat, messages))
                elif anno.get_value() == KindSubs.CONSTR:
                    if pat.get_kind() == KindMsg.VAR:
                        if pat in vars_to_be_filled:
                            assert pat.sized
                            list_of_dicts = [{pat: m} for m in all_messages_of_size(messages, pat.size)]
                            results.append(list_of_dicts)
                        else:
                            results.append([dict({})])
                    elif pat.is_message():
                        results.append([dict({})])
                    else:
                        to_visit.append((False, anno, pat))
                        if pat.is_two_ary_msg():
                            to_visit.append((True, anno.right, pat.second))
                            to_visit.append((True, anno.left, pat.first))
                        else:
                            raise Exception("Out of Options")
                else:
                    raise Exception("BasicMsg should be a message")
            else:
                assert (pat.get_kind() == KindMsg.ENC) | (pat.get_kind() == KindMsg.PAIR)
                right = results.pop()
                left = results.pop()
                substitutions_combined = combine_lists_of_substitutions(left, right)
                substitutions_eligible = []
                if pat.get_kind() == KindMsg.ENC:
                    substitutions_eligible = get_eligible_substitutions(pat, messages)
                substitutions = substitutions_combined + substitutions_eligible
                results.append(substitutions)
        assert len(results) == 1
        # Unify list of substitutions
        list_substs = []
        for subst in results[0]:
            if subst not in list_substs:
                list_substs.append(subst)
        return list_substs


class KindSubs(Enum):
    BOTTOM = 0
    CONSTR  = 1
    ELIGIBLE = 2
