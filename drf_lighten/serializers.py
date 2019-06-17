import operator

from django.utils.translation import ugettext


class DynamicFieldsMixin(object):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        if fields and exclude:
            raise Exception(ugettext(
                "You can't enable 'fields' AND 'exclude' at the same time"
            ))

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        if fields:
            self.lighten(fields, 'fields')
        elif exclude:
            self.lighten(exclude, 'exclude')

    def lighten(self, entries, argument):
        if argument == 'fields':
            field_selector = operator.sub
        else:
            field_selector = operator.and_

        field_strings, field_dictionary = self.split_fields(entries)

        for field_name, field_entry in field_dictionary.items():
            self.pass_down_structure(field_name, field_entry, argument)

        subset = set(field_strings)
        never_pop = set(field_dictionary.keys())
        existing = set(self.fields.keys())

        for field_name in field_selector(existing, subset) - never_pop:
            self.fields.pop(field_name, None)

    def split_fields(self, fields):
        strings = []
        dictionary = {}

        for field_entry in fields:
            if isinstance(field_entry, dict):
                dictionary.update(field_entry)
            if isinstance(field_entry, basestring):
                strings.append(field_entry)

        return strings, dictionary

    def get_field_and_kwargs(self, field_name):
        field = self.fields[field_name]
        many = getattr(field, 'many', False)
        field = getattr(field, 'child', field)

        inherit = ('instance', 'data', 'partial', 'context',  # 'many',
                   'read_only', 'write_only', 'required', 'default',
                   'source', 'initial', 'label', 'help_text', 'style',
                   'error_messages', 'validators', 'allow_null')
        kwargs = {
            attribute_name: getattr(field, attribute_name, None)
            for attribute_name in inherit
        }
        kwargs['many'] = many

        if kwargs['source'] in ['', field_name]:
            kwargs.pop('source')

        return field, kwargs

    def pass_down_structure(self, field_name, field_entry, arg_name):
        field, kwargs = self.get_field_and_kwargs(field_name)
        kwargs[arg_name] = field_entry
        if not hasattr(field, 'fields'):
            return
        self.fields[field_name] = field.__class__(**kwargs)
