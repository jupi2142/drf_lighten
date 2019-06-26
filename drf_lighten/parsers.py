import json
import re


def re_parser(string):
    step_0 = string.replace(' ', '').replace('{', '[').replace('}', ']')
    step_1 = re.sub(r'(\w+)\{', r'{"\1": [', step_0)
    step_2 = re.sub(r'(\w+)\[', r'{"\1": [', step_1)
    step_3 = re.sub(r'](?=.)', r']}', step_2)
    step_4 = re.sub(r'(?<=\[|,)(\*|\w+)(?=,|])', r'"\1"', step_3)
    return json.loads(step_4)


def recursive_parser(string):
    pass


def validate_star(parsed):
    strings = []
    dictionary = {}

    for field_entry in parsed:
        if isinstance(field_entry, dict):
            dictionary.update(field_entry)
        else:
            strings.append(field_entry)

    if '*' in strings and len(strings) != 1:
        raise ValueError

    for inner_entry in dictionary.values():
        validate_star(inner_entry)


def parse(string):
    try:
        parsed = json.loads(string)
    except (ValueError, TypeError):
        parsed = re_parser(string)

    validate_star(parsed)
    return parsed
