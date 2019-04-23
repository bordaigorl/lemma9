class IdentifierManager(object):

    def __init__(self, start_id = 0):
        self.next_id = start_id

    def next(self):
        self.next_id += 1
        return self.next_id - 1

    def next_n(self, n):
        ret = xrange(self.next_id, self.next_id + n)
        self.next_id += n
        return ret

    def get_identifiers(self):
        return set(xrange(self.next_id))

    def all_ids(self):
        return set(xrange(self.next_id))
