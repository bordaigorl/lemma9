from enum import Enum
from z3 import *


class KindMsg(Enum):
    BASIC = 1
    PAIR  = 2
    ENC   = 3
    AENC  = 4
    ADEC  = 5
    SIGN  = 6
    VERI  = 7
    PUB   = 8
    VAR   = 9


class Message:
    def __str__(self):
        raise Exception('No!')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self):
        raise Exception('To be implemented in subclasses')

    def get_kind(self):
        raise Exception('Message should not be instantiated')

    def get_names(self):
        raise Exception()

    def get_size(self):
        raise Exception()

    def get_comps(self):
        raise Exception('Try to get components of Message')

    def get_conds(self, matching, msgs):
        raise Exception('Try to get conditions of Message')

    def get_split_conds(self, matching, msgs):
        M = FreshBool(str(self))
        result = []
        for m2 in msgs:
            pairs_for_equalities = self.equalities_for_split_msgs(m2)
            if pairs_for_equalities != False:
                equalities_m2 = []
                for (x, y) in pairs_for_equalities:
                    equalities_m2.append(y == matching[x])
                result.append(And(equalities_m2))
            else:
                result.append(False)
        return M, Implies(M, Or(result))

    def is_message(self):
        raise Exception()

    def rename(self, renamer):
        raise Exception()

    def unpub(self):
        raise Exception('Cannot get private key from non-public key!')

    def substitute_variables(self, substitutions):
        raise Exception()

    def is_two_ary_msg(self):
        return False


class BasicMsg(Message):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def str_tex(self):
        return self.name.str_tex()

    def __hash__(self):
        return hash(self.name)

    def get_kind(self):
        return KindMsg.BASIC

    def get_names(self):
        return set([self.name])

    def get_size(self):
        return 1

    def get_conds(self, matching, msgs):
        conditions = []
        booleans = []
        for m in msgs:
            if m.get_kind() == KindMsg.BASIC:
                B = FreshBool(str(self.name) + "->" + str(m.name))
                booleans.append(B)
                conditions.append(Implies(B, matching[self.name] == m.name))
        M = FreshBool(str(self))
        conditions.append(Implies(M, Or(booleans)))
        return M, conditions

    def get_split_conds(self, matching, msgs):
        raise Exception('Split conds for basicmsg')

    def is_message(self):
        return True

    def equalities_for_split_msgs(self, msg):
        if msg.get_kind() == KindMsg.BASIC:
            return [(self.name, msg.name)]
        else:
            return False

    def rename(self, renamer):
        return BasicMsg(renamer.get(self.name, self.name))

    def get_variables(self):
        return set()

    def substitute_variables(self, substitutions):
        return self

    def get_msg_to_match(self):
        return self


class TwoAryMsg(Message):

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def get_kind(self):
        raise Exception('TwoAryMsg is abstract')

    def get_names(self):
        return self.first.get_names() | self.second.get_names()

    def get_size(self):
        return max(self.first.get_size(), self.second.get_size()) + 1

    def get_variables(self):
        return self.first.get_variables() | self.second.get_variables()

    def get_comps(self):
        return [self.first, self.second]

    def is_message(self):
        return self.first.is_message() & self.second.is_message()

    def get_conds(self, matching, msgs):
        conditions = []
        split = FreshBool(str(self) + '_split')
        combo = FreshBool(str(self) + '_combo')

        M = FreshBool(str(self))
        conditions.append(Implies(M, Or(split, combo)))

        split_conds = self.get_split_conds(matching, msgs)
        conditions.append(Implies(split, split_conds[0]))
        conditions.append(split_conds[1])

        combo1 = FreshBool(str(self) + '_combo1')
        combo2 = FreshBool(str(self) + '_combo2')
        conditions.append(Implies(combo, And(combo1, combo2)))
        comps = self.get_comps()
        # if comps[0].get_kind() != KindMsg.BASIC:
        combo1conds = comps[0].get_conds(matching, msgs)
        conditions.append(Implies(combo1, combo1conds[0]))
        conditions.extend(combo1conds[1])
        # if comps[1].get_kind() != KindMsg.BASIC:
        combo2conds = comps[1].get_conds(matching, msgs)
        conditions.append(Implies(combo2, combo2conds[0]))
        conditions.extend(combo2conds[1])

        # If one of them is basic, it is taken care of that it is satisfied
        # so combo1/2 can live w/o constraints
        return M, conditions

    def equalities_for_split_msgs(self, msg):
        equalities = []
        if msg.get_kind() == self.get_kind():
            comps = msg.get_comps()
            equalities1 = self.first.equalities_for_split_msgs(comps[0])
            equalities2 = self.second.equalities_for_split_msgs(comps[1])
            if (equalities1 == False) | (equalities2 == False):
                return False
            else:
                equalities.extend(equalities1)
                equalities.extend(equalities2)
                return equalities
        else:
            return False

    def rename(self, renamer):
        return self.__class__(self.first.rename(renamer), self.second.rename(renamer))

    def substitute_variables(self, substitutions):
        return self.__class__(self.first.substitute_variables(substitutions), self.second.substitute_variables(substitutions))

    def get_msg_to_match(self):
        return self.__class__(self.first.get_msg_to_match(), self.second.get_msg_to_match())

    def is_two_ary_msg(self):
        return True


class EncMsg(TwoAryMsg):

    def __init__(self, msg, key):
        TwoAryMsg.__init__(self, msg, key)

    def __str__(self):
        return "{" + str(self.first) + "}_" + str(self.second)

    def str_tex(self):
        return "\\enc{" + self.first.str_tex() + "}{" + self.second.str_tex() + "}"

    def __hash__(self):
        return hash((self.first, self.second))*2

    def get_kind(self):
        return KindMsg.ENC


class AEncMsg(EncMsg):
    def __init__(self, msg, key):
        # key might be a variable and therefore no restriction here
        # if not isinstance(key, PublicKeyMsg):
        #     raise Exception('Asymmetric encryption without public key')
        EncMsg.__init__(self, msg, key)

    def __str__(self):
        return 'aenc(' + str(self.first) + ", " + str(self.second) + ')'

    def get_kind(self):
        return KindMsg.AENC


class SignMsg(EncMsg):
    def __init__(self, msg, key):
        # key might be not a public key for certificates
        # if not isinstance(key, PublicKeyMsg):
        #     raise Exception('Asymmetric encryption without public key')
        EncMsg.__init__(self, msg, key)

    def __str__(self):
        return 'sign(' + str(self.first) + ", " + str(self.second) + ')'

    def get_kind(self):
        return KindMsg.SIGN


class PublicKeyMsg(Message):

    def __init__(self, private_key):
        self.private = private_key

    def __str__(self):
        return 'pub(' + str(self.private) + ')'

    def __hash__(self):
        return hash(self.private) + 1

    def get_kind(self):
        return KindMsg.PUB

    def get_names(self):
        return self.private.get_names()

    def get_size(self):
        return 1 + self.private.get_size()

    def is_message(self):
        return self.private.is_message()

    def unpub(self):
        return self.private

    def get_conds(self, matching, msgs):
        conditions = []
        split = FreshBool(str(self) + '_split')
        combo = FreshBool(str(self) + '_combo')

        M = FreshBool(str(self))
        conditions.append(Implies(M, Or(split, combo)))

        split_conds = self.get_split_conds(matching, msgs)
        conditions.append(Implies(split, split_conds[0]))
        conditions.append(split_conds[1])

        comboconds = self.private.get_conds(matching, msgs)
        conditions.append(Implies(combo, comboconds[0]))
        conditions.extend(comboconds[1])

        return M, conditions

    def equalities_for_split_msgs(self, msg):
        if msg.get_kind() == KindMsg.PUB:
            equalities = self.private.equalities_for_split_msgs(msg.private)
            return equalities
        else:
            return False

    def rename(self, renamer):
        return PublicKeyMsg(self.private.rename(renamer))

    def substitute_variables(self, substitutions):
        return PublicKeyMsg(self.private.substitute_variables(substitutions))

    def get_msg_to_match(self):
        return PublicKeyMsg(self.private.get_msg_to_match())

    def get_variables(self):
        return self.private.get_variables()


class PairMsg(TwoAryMsg):
    def __init__(self, first, second):
        TwoAryMsg.__init__(self, first, second)

    def __str__(self):
        return "(" + str(self.first) + ", " + str(self.second) + ")"

    def str_tex(self):
        first_repr = self.first.str_tex()
        if self.first.get_kind() == KindMsg.PAIR:
            first_repr = first_repr[1:-1] + ", "
        second_repr = self.second.str_tex()
        if self.second.get_kind() == KindMsg.PAIR:
            second_repr = second_repr[1:-1]
        return "(" + first_repr + ", " + second_repr + ")"

    def __hash__(self):
        return hash((self.first, self.second))

    def get_kind(self):
        return KindMsg.PAIR

    def get_split_conds(self):
        raise Exception('Split on pairs should not happen!')

    def get_conds(self, matching, msgs):
        # for pairs, we do not need a split check but only a combo where we check for both components
        conditions = []
        M = FreshBool(str(self))
        combo1 = FreshBool(str(self) + '_combo1')
        combo2 = FreshBool(str(self) + '_combo2')
        conditions.append(Implies(M, And(combo1, combo2)))
        comps = self.get_comps()
        combo1conds = comps[0].get_conds(matching, msgs)
        conditions.append(Implies(combo1, combo1conds[0]))
        conditions.extend(combo1conds[1])
        combo2conds = comps[1].get_conds(matching, msgs)
        conditions.append(Implies(combo2, combo2conds[0]))
        conditions.extend(combo2conds[1])
        return M, conditions

