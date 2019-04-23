class NameRepr(object):
    def __init__(self, name):
        self.name = name
        # self.id = id

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        # does not check for size!
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def __str__(self):
        return str(self.name)

    def str_tex(self):
        if len(self.name) > 1:
            return self.name[0] + '_{' + self.name[1:] + '}'
        return str(self.name)
