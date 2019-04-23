class BscAnnotation(object):
    def __init__(self, annotation):
        self.annotation = annotation

    def get_bool(self):
        return bool(self.annotation)

    def get_value(self):
        return self.annotation

    def str(self, level):
        return '\t'*level + str(self.annotation) + '\n'

    def __str__(self):
        return str(self.annotation)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class StrAnnotation(BscAnnotation):
    def __init__(self, annotation, left, right):
        BscAnnotation.__init__(self, annotation)
        self.left = left
        self.right = right

    def __str__(self):
        return self.str(0)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def str(self, level):
        ret = self.right.str(level+1)
        ret += '\t'*level + str(self.annotation) + '\n'
        ret += self.left.str(level+1)
        return ret
