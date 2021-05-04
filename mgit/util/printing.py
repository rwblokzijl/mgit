from typing import Iterable
from six import string_types

def is_iterable(arg):
    return ( isinstance(arg, Iterable) and not isinstance(arg, string_types))

def indent_str(string: str, indent: int=2) -> str:
    return (" " * indent) + string.strip('\n').replace('\n', '\n' + ' ' * indent)

def collapse(gen):
    return "\n".join(gen)

def pretty_string(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if '\n' not in collapse(pretty_string(value)):
                yield str(key) + " = " + str(value or "")
            else:
                yield str(key) + ":"
                for element in pretty_string(value):
                    yield indent_str(element)
    elif is_iterable(data):
        for value in data:
            yield from pretty_string(value)
    elif data is None:
        pass
    else:
        yield str(data)

