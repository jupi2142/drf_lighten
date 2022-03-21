from collections import defaultdict
import json
import re
from abc import ABC, abstractmethod
from typing import List

from drf_lighten.exceptions import ParserException
from drf_lighten.types import Structure


class OldParser(ABC):
    @abstractmethod
    def parse(self, string: str) -> Structure:
        ...


class JSONParser(OldParser):
    def parse(self, string: str) -> Structure:
        try:
            return json.loads(string)
        except json.JSONDecodeError:
            raise ParserException


class PseudoJSONParser(OldParser):
    def parse(self, string: str) -> Structure:
        step_0 = string.replace(" ", "").replace("{", "[").replace("}", "]")
        step_1 = re.sub(r"(\w+)\{", r'{"\1": [', step_0)
        step_2 = re.sub(r"(\w+)\[", r'{"\1": [', step_1)
        step_3 = re.sub(r"](?=.)", r"]}", step_2)
        step_4 = re.sub(r"(?<=\[|,)(\*|\w+)(?=,|])", r'"\1"', step_3)
        try:
            return json.loads(step_4)
        except json.JSONDecodeError:
            raise ParserException


class DotParser(OldParser):
    def parse(self, string: str) -> Structure:
        first_split = sorted(string.strip(".,").split(","), key=len)
        second_split = [s.split(".", 1) for s in first_split]

        self_ = []
        nested = defaultdict(list)

        for split in second_split:
            if len(split) == 1:
                self_.append(split[0])
            else:
                parent, child = split
                nested[parent].append(child)

        for key, value in nested.items():
            sub_string = ",".join(value)
            if "." in sub_string:
                nested[key] = self.parse(sub_string)

        if nested:
            self_.append(dict(nested))
        return self_


class OldChainParser(OldParser):
    def __init__(self, parsers: List[OldParser]):
        self.parsers = parsers

    def parse(self, string: str) -> Structure:
        for parser in self.parsers:
            try:
                return parser.parse(string)
            except ParserException:
                continue

        raise ParserException
