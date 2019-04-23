class Definition:
    definitions = dict()

    def __init__(self, proccall, actions):
        boundnames = set()
        for a in actions:
            boundnames.update(a.get_boundnames())
        if proccall.get_names() & boundnames:
            raise Exception('Name clash of process call and actions')
        self.proccall = proccall
        self.actions = actions
        self.definitions[proccall.label] = self

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __str__(self):
        repactions = " + ". join(str(x) for x in self.actions)
        return str(self.proccall) + ' := ' + repactions

    def str_tex(self):
        repactions = " \\; + \\; \\\\ \n & &". join(x.str_tex() for x in self.actions)
        return self.proccall.str_tex() + ' & := & ' + repactions

    def get_globalnames(self):
        freenames = set()
        for a in self.actions:
            freenames.update(a.get_freenames())
        return freenames

    def rename_name_repr(self, repr_man):
        map(lambda action: action.rename_name_repr(repr_man), self.actions)

    def rename(self, substitution):
        # maybe rename proccall as well
        actions = map(lambda action: action.rename(substitution), self.actions)
        return Definition(self.proccall, actions)
