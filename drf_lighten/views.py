from .settings import Setting
from .request_parsers import OldRequestParser, RequestParser

setting = Setting()


class DynamicStructureMixin:
    parser: RequestParser = RequestParser(setting.struct)

    def get_serializer(self, *args, **kwargs):
        kwargs["structure"] = self.parser.parse(self.request)
        return super(DynamicStructureMixin, self).get_serializer(
            *args, **kwargs
        )


class DynamicFieldsMixin:
    include_parser: OldRequestParser = OldRequestParser(setting.include)
    exclude_parser: OldRequestParser = OldRequestParser(setting.exclude)

    def get_serializer(self, *args, **kwargs):
        kwargs["fields"] = self.include_parser.parse(self.request)
        kwargs["exclude"] = self.exclude_parser.parse(self.request)
        return super(DynamicFieldsMixin, self).get_serializer(*args, **kwargs)
