from Message import *
from Variable import *
from Definition import *
from helper import split_string_into_letters_and_numbers


class ProcessCall:
    definitions = dict()

    def __init__(self, label, parameters=tuple(), id=None, ids=None):
        if isinstance(parameters, Message) | isinstance(parameters, Variable):
            parameters = (parameters, )
        if len(parameters) != 0:
            if filter(lambda p: ((not isinstance(p, Message)) & (not isinstance(p, Variable))), parameters):
                raise Exception('Process call with parameters different from messages')
            for p in filter(lambda p: isinstance(p, Variable), parameters):
                if p.sized:
                    raise Exception('sized variable in process call parameters')
        if self.definitions.has_key(label):
            if len(parameters) != self.definitions.get(label):
                # print label
                raise Exception('Second use of process identifier with different number of parameters!')
        else:
            self.definitions[label] = len(parameters)
        self.label = label
        self.parameters = parameters
        self.id = id
        self.ids = ids
        self.subst_actions = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self):
        return hash((self.label, self.parameters))

    def __str__(self):
        repparameter = ", ".join(str(x) for x in self.parameters)
        replist = "[" + repparameter + "]" if repparameter else repparameter
        return self.label + replist

    def str_tex(self):
        repparameter = ", ".join(x.str_tex() for x in self.parameters)
        replist = "[" + repparameter + "]" if repparameter else repparameter
        letters, numbers = split_string_into_letters_and_numbers(self.label)
        if letters is None:
            raise Exception('Process call should always have at least one letter')
        if numbers is None:
            return str(letters) + str(replist)
        return str(letters) + '_{' + numbers + '}' + str(replist)

    def get_label(self):
        return self.label

    def get_parameters(self):
        return self.parameters

    def get_names(self):
        names = set()
        for p in self.parameters:
            names.update(p.get_names())
        return names

    def get_variables(self):
        variables = set()
        for p in self.parameters:
            variables.update(p.get_variables())
        return variables

    def get_substituted_actions(self, knowledge = []):
        if not self.subst_actions:
            definition = Definition.definitions.get(self.label, None)
            if not definition:
                raise Exception('Definition not found')
            subs = dict(zip(definition.proccall.parameters, self.parameters))
            # When using knowledge, then not possible to buffer them anymore
            self.subst_actions = [action.substitute_variables(subs, knowledge) for action in definition.actions]
        return self.subst_actions

    def rename(self, renamer):
        new_params = []
        for p in self.parameters:
            new_params.append(p.rename(renamer))
        return ProcessCall(self.label, tuple(new_params), self.id)

    def substitute_variables(self, substitutions):
        new_params = [p.substitute_variables(substitutions) for p in self.parameters]
        return ProcessCall(self.label, tuple(new_params))

    def mark_with_id(self, id_man):
        self.id = id_man.next()

    def get_extension_factor_and_annotations(self, messages):
        return [a.get_extension_factor_and_annotation(messages) for a in self.get_substituted_actions()]

