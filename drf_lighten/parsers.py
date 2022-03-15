import json
import re
from abc import ABC, abstractmethod
from typing import List

from .exceptions import ParserException
from .types import Structure


class Parser(ABC):
    @abstractmethod
    def parse(self, string: str) -> Structure:
        ...


class JSONParser(Parser):
    def parse(self, string: str) -> Structure:
        try:
            return json.loads(string)
        except json.JSONDecodeError:
            raise ParserException


class RegExpParser(Parser):
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


class RecursiveParser(Parser):
    def parse(self, string: str) -> Structure:
        ...


class ChainParser(Parser):
    def __init__(self, parsers: List[Parser]):
        self.parsers = parsers

    def parse(self, string: str) -> Structure:
        for parser in self.parsers:
            try:
                return parser.parse(string)
            except ParserException:
                continue

        raise ParserException


default_parser = ChainParser([JSONParser(), RegExpParser()])


def validate_star(parsed):
    strings, dictionary = split(parsed)

    for inner_entry in dictionary.values():
        validate_star(inner_entry)

    if "*" in strings and len(strings) != 1:
        raise ValueError
