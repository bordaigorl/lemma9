from PiLexer import *
from PiParser import *
from Listener import *
from Program import *


def parse_input(input):
    lexer = PiLexer(input)
    stream = CommonTokenStream(lexer)
    parser = PiParser(stream)
    tree = parser.program()
    listener = Listener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    assert len(listener.state) == 0
    program = Program(listener.definitions, listener.limit, listener.helpers)
    return program


def get_program_from_file_input(file_name):
    f = open(file_name)
    to_parse = InputStream(f.read())
    return parse_input(to_parse)
