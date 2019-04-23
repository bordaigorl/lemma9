# helper.py


def split_string_into_letters_and_numbers(s):
    return (''.join(c for c in s if c.isalpha()) or None,
            ''.join(c for c in s if c.isdigit()) or None)