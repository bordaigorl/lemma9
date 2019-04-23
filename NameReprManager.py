from IdentifierManager import *
from NameRepr import *


class NameReprManager(IdentifierManager):

    def __init__(self, start_id = 0):
        self.still_renaming = True
        IdentifierManager.__init__(self, start_id)
        self.map_id_repr = dict()
        self.map_repr_id = dict()

    def get_substitution_for_set(self, reprs):
        list_of_reprs = list(reprs)
        list_of_ids = self.next_n(len(list_of_reprs))
        dict_repr_id = dict(zip(list_of_reprs, list_of_ids))
        for (k, v) in dict_repr_id.iteritems():
            self.map_id_repr[v] = k
            if not isinstance(k, int): # then it is repr
                self.map_repr_id[k] = v
        return dict_repr_id

    def finish_renaming(self):
        self.still_renaming = False

    def add_connection(self, old_id, new_id):
        assert self.still_renaming
        self.map_id_repr[new_id] = old_id
        if not isinstance(old_id, int):
            self.map_repr_id[old_id] = new_id

    def get_num_repr(self, identifier):
        representative = self.get_repr(identifier)
        return self.map_repr_id[representative]

    def get_repr(self, identifier):
        repr = self.map_id_repr.get(identifier, identifier)
        if repr != identifier:
            result = self.get_repr(repr)
            self.map_id_repr[identifier] = result
            return result
        else:
            return repr

    def get_num_substitution(self):
        substitution = dict()
        for k in self.map_id_repr.iterkeys():
            substitution[k] = self.get_num_repr(k)
        return substitution

    def get_substitution_with_ids(self):
        substitution = dict()
        for k in self.map_id_repr.iterkeys():
            substitution[k] = NameRepr(str(self.get_repr(k)) + str(k))
        return substitution

    def get_substitution_without_ids(self):
        substitution = dict()
        for k in self.map_id_repr.iterkeys():
            substitution[k] = NameRepr(str(self.get_repr(k)))
            # maybe check for clashes there?
        return substitution

    def prettify(self, limit):
        substitution = self.get_substitution_with_ids()
        pretty_limit = limit.rename(substitution)
        return str(pretty_limit)

    def translate_error_back(self, error):
        return error.rename(self.get_substitution_with_ids())
        # return tuple([self.prettify(x) for x in error])

    def translate_back_to_num(self, to_translate):
        substitution = self.get_num_substitution()
        return to_translate.rename(substitution)

