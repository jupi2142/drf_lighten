from typing import Set

from django.conf import settings

from .exceptions import ParserException
from .parsers import Parser, default_parser
from .settings import Setting


class DynamicFieldsMixin:
    parser: Parser = default_parser
    setting: Setting = Setting()

    def get_serializer(self, *args, **kwargs):
        if self.setting.include in self.request.query_params:
            raw_structure = self.request.query_params[self.setting.include]
            kwargs["fields"] = self.parser.parse(raw_structure)
        elif self.setting.exclude in self.request.query_params:
            raw_structure = self.request.query_params[self.setting.exclude]
            kwargs["exclude"] = self.parser.parse(raw_structure)

        return super(DynamicFieldsMixin, self).get_serializer(*args, **kwargs)
