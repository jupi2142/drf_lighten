from abc import ABC, abstractmethod
from typing import List

from drf_lighten.exceptions import ParserException


class Parser(ABC):
    @abstractmethod
    def parse(self, string: str) -> dict:
        ...


class UnifiedParser(Parser):
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

    def parse(self, string: str) -> dict:
        for parser in self.parsers:
            try:
                return parser.parse(string)
            except ParserException:
                continue

        raise ParserException
