import json
import re


def re_parser(string):
    step_0 = string.replace(' ', '').replace('{', '[').replace('}', ']')
    step_1 = re.sub(r'(\w+)\{', r'{"\1": [', step_0)
    step_2 = re.sub(r'(\w+)\[', r'{"\1": [', step_1)
    step_3 = re.sub(r'](?=.)', r']}', step_2)
    step_4 = re.sub(r'(?<=\[|,)(\w+)(?=,|])', r'"\1"', step_3)
    return json.loads(step_4)


def recursive_parser(string):
    pass


def parse(string):
    try:
        return json.loads(string)
    except (ValueError, TypeError):
        pass

    return re_parser(string)
