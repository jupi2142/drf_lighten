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


class DotParser(Parser):
    def parse(self, string: str) -> Structure:
        ...


class StackParser(Parser):
    def new_field(self, type_: str):
        return {
            "type": type_,
            "fields": {
                "self": [],
                "nested": {},
            },
        }

    def parse(self, string: str) -> dict:
        stack = []
        for index, char in enumerate(string):
            if char.isspace():
                continue
            if char == "{":
                field = self.new_field(
                    "omit" if string[index - 1] == "-" else "keep"
                )
                stack.append(field)
            elif char == "}":
                if len(stack) == 1:
                    if stack[0]["fields"]["self"][-1].startswith("-"):
                        raise ParserException("Syntax Error")
                    return stack[0]
                nested_field = stack.pop()
                nested_key = stack[-1]["fields"]["self"].pop()
                if nested_key.startswith("-"):
                    nested_field["type"] = "omit"
                stack[-1]["fields"]["nested"][
                    nested_key.strip("-")
                ] = nested_field
            elif (
                char.isalpha()
                or char == "_"
                or (
                    char == "-"
                    and index < len(string) + 1
                    and string[index + 1].isalpha()
                )
            ):
                if len(stack) == 0:
                    raise ParserException("Syntax Error")
                try:
                    stack[-1]["fields"]["self"][-1] += char
                except IndexError:
                    stack[-1]["fields"]["self"].append(char)
            elif char == ",":
                try:
                    last_self = stack[-1]["fields"]["self"][-1]
                except IndexError:
                    continue
                if last_self.startswith("-"):
                    raise ParserException("Syntax Error")
                stack[-1]["fields"]["self"].append("")
            elif char == "~":
                ...

        raise ParserException("Syntax Error")


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
