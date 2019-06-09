from rest_framework import serializers
from operator import and_, sub


class DynamicFieldsMixin(object):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        error_message = (
            "You can't enable 'fields' AND 'exclude' at the same time"
        )

        if fields and exclude:
            raise Exception(error_message)

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        if not (fields or exclude):
            return

        field_selector = sub if fields else and_
        field_entries = fields or exclude
        field_strings, field_dictionaries = self.split_fields(field_entries)
        argument = 'fields' if fields else 'exclude'

        subset = set(field_strings)
        existing = set(self.fields.keys())

        for field_name in field_selector(existing, subset):
            self.fields.pop(field_name, None)

        for field_entry in field_dictionaries:
            self.pass_down_structure(field_entry, argument)

    def split_fields(self, fields):
        strings = []
        dictionaries = []

        for field_entry in fields:
            if isinstance(field_entry, dict):
                dictionaries.append(field_entry)
            if isinstance(field_entry, basestring):
                strings.append(field_entry)

        return strings, dictionaries

    def get_field_and_kwargs(self, field_name):
        field = self.fields[field_name]
        many = isinstance(field, serializers.ListSerializer)
        field = getattr(field, 'child', field)

        inherit = ('instance', 'data', 'partial', 'context',  # 'many',
                   'read_only', 'write_only', 'required', 'default',
                   'source', 'initial', 'label', 'help_text', 'style',
                   'error_messages', 'validators', 'allow_null')
        kwargs = {
            attribute_name: getattr(field, attribute_name)
            for attribute_name in inherit
        }
        kwargs['many'] = many

        if kwargs['source'] in ['', field_name]:
            kwargs.pop('source')

        return field, kwargs

    def pass_down_structure(self, field_entry, arg_name):
        if not field_entry.keys():
            return

        field_name = field_entry.keys().pop()
        field, kwargs = self.get_field_and_kwargs(field_name)
        kwargs[arg_name] = field_entry[field_name]
        self.fields[field_name] = field.__class__(**kwargs)
