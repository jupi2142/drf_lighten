from dataclasses import dataclass
from typing import Optional

from rest_framwwork.request import Request

from .parsers import (
    Parser,
    OldParser,
    UnifiedParser,
    DotParser,
    JSONParser,
    OldChainParser,
    PseudoJSONParser,
)
from .types import Structure
from .settings import Setting


@dataclass
class OldRequestParser:
    query_param: str
    parser: OldParser = OldChainParser(
        [JSONParser(), PseudoJSONParser(), DotParser()]
    )

    def parse(self, request: Request) -> Optional[Structure]:
        if self.query_param in request.query_params:
            raw_structure = request.query_params[self.query_param]
            return self.parser.parse(raw_structure)


include_request_parser = OldRequestParser(query_param=Setting().include)

exclude_request_parser = OldRequestParser(query_param=Setting().exclude)


@dataclass
class RequestParser:
    query_param: str = Setting().struct
    parser: Parser = UnifiedParser()

    def parse(self, request: Request) -> Optional[dict]:
        if self.query_param in request.query_params:
            raw_structure = request.query_params[self.query_param]
            return self.parser.parse(raw_structure)
