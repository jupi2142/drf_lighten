from rest_framework import serializers


class DynamicFieldsMixin(object):
    """
    A ModelSerializer that takes additional `fields` and `exclude` arguments
    that controls which fields should[ not] be displayed.
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        error_message = (
            "You can't enable 'fields' AND 'exclude' at the same time"
        )

        if fields and exclude:
            raise Exception(error_message)

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        if fields is not None:
            field_names = self.get_dynamic_field_names(fields)

            subset = set(field_names)
            existing = set(self.fields.keys())
            for field_name in existing - subset:
                self.fields.pop(field_name, None)

            for field_entry in fields:
                if isinstance(field_entry, dict):
                    self.distribute_dictionary(field_entry, 'fields')

        elif exclude is not None:
            for field_entry in exclude:
                if isinstance(field_entry, dict):
                    self.distribute_dictionary(field_entry, 'exclude')
                else:
                    self.fields.pop(field_entry, None)

    def get_dynamic_field_names(self, fields):
        return [
            field_entry.keys()[0]
            if isinstance(field_entry, dict)
            else field_entry

            for field_entry in fields
        ]

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
