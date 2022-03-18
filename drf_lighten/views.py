from typing import Optional

from django.conf import settings

from .parsers import Parser, StackParser, default_parser
from .settings import Setting


class DynamicStructureMixin:
    parser: Optional[Parser] = None
    setting: Setting = Setting()

    def get_parser(self):
        if self.parser:
            return self.parser
        return StackParser()

    def get_serializer(self, *args, **kwargs):
        if self.setting.struct in self.request.query_params:
            raw_structure = self.request.query_params[self.setting.struct]
            kwargs["structure"] = self.get_parser().parse(raw_structure)

        return super(DynamicStructureMixin, self).get_serializer(
            *args, **kwargs
        )


class DynamicFieldsMixin:
    parser: Optional[Parser] = None
    setting: Setting = Setting()

    def get_parser(self):
        if self.parser:
            return self.parser
        return default_parser

    def get_serializer(self, *args, **kwargs):
        if self.setting.include in self.request.query_params:
            raw_structure = self.request.query_params[self.setting.include]
            kwargs["fields"] = self.get_parser().parse(raw_structure)
        if self.setting.exclude in self.request.query_params:
            raw_structure = self.request.query_params[self.setting.exclude]
            kwargs["exclude"] = self.get_parser().parse(raw_structure)

        return super(DynamicFieldsMixin, self).get_serializer(*args, **kwargs)
