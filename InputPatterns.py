from Message import AEncMsg, SignMsg, PublicKeyMsg


class ADecPattern:

    def __init__(self, to_decr, private_key):
        self.to_decr = to_decr
        self.private_key = private_key

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __str__(self):
        return "adec(" + str(self.to_decr) + ", " + str(self.private_key) + ")"

    def get_msg_to_match(self):
        return AEncMsg(self.to_decr, PublicKeyMsg(self.private_key))

    def get_variables(self):
        return self.to_decr.get_variables() | self.private_key.get_variables()

    def substitute_variables(self, substitutions):
        return ADecPattern(self.to_decr.substitute_variables(substitutions), self.private_key.substitute_variables(substitutions))

    def is_message(self):
        return self.to_decr.is_message() & self.private_key.is_message()

    def is_two_ary(self):
        return True


class VeriPattern:

    def __init__(self, to_veri, public_key):
        self.to_veri = to_veri
        self.public_key = public_key

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __str__(self):
        return "veri(" + str(self.to_veri) + ", " + str(self.public_key) + ")"

    def get_msg_to_match(self):
        private_key = self.public_key.unpub()
        return SignMsg(self.to_veri, private_key)

    def get_variables(self):
        return self.to_veri.get_variables() | self.public_key.get_variables()

    def substitute_variables(self, substitutions):
        return VeriPattern(self.to_veri.substitute_variables(substitutions), self.public_key.substitute_variables(substitutions))

    def is_message(self):
        return self.to_veri.is_message() & self.public_key.is_message()

    # def is_two_ary(self):
    #     return True
    # not needed as converted to msg_to_match before
