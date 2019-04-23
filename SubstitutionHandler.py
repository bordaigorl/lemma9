from Message import *
from collections import defaultdict


def get_substitution(pat, message):
    substitutions = defaultdict(lambda : None, {})
    listofpairs = [(pat, message)]
    while listofpairs:
        pat, message = listofpairs.pop()
        # if pat.is_message() == message.is_message():
        #     if pat != message:
        #         return False, None
        if (pat.get_kind() == KindMsg.BASIC) & (message.get_kind() == KindMsg.BASIC):
            if pat.name != message.name:
                return False, None
        elif pat.get_kind() == KindMsg.VAR:
            if substitutions[pat] is None:
                # Inplace-check whether size function is respected
                if pat.sized:
                    if message.get_size() <= pat.size:
                        substitutions[pat] = message
                    else:
                        return False, None
                else:
                    substitutions[pat] = message
            elif substitutions[pat] != message:
                return False, None
        elif pat.is_two_ary_msg() & message.is_two_ary_msg() & (pat.get_kind() == message.get_kind()):
            listofpairs.append((pat.first, message.first))
            listofpairs.append((pat.second, message.second))
        elif (pat.get_kind() == KindMsg.PUB) & (message.get_kind() == KindMsg.PUB):
            listofpairs.append((pat.private, message.private))
        else:
            return False, None
    return True, substitutions


def get_eligible_substitutions(pat, messages):
    substitutions = []
    for m in messages:
        eligible, substitution = get_substitution(pat, m)
        if eligible:
            substitutions.append(substitution)
    return substitutions


def combine_lists_of_substitutions(list1, list2):
    return filter(lambda x: x is not None, [combine_two_substitutions(s1, s2) for s1 in list1 for s2 in list2])


def combine_two_substitutions(substitution1, substitution2):
    keys1 = set(substitution1.iterkeys())
    keys2 = set(substitution2.iterkeys())
    common_keys = keys1 & keys2
    for k in common_keys:
        if not (substitution1[k] == substitution2[k]):
            return None
    result = dict(substitution1)
    result.update(substitution2)
    return result


def check_for_eligible_message(pat, messages):
    for msg in messages:
        eligible, _ = get_substitution(pat, msg)
        if eligible:
            return True
    return False
