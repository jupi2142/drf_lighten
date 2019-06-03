import json
from rest_framework import serializers


class DynamicFieldsMixin(object):
    """
    A ModelSerializer that takes additional `fields` and `exclude` arguments
    that controls which fields should[ not] be displayed.
    """

    def __init__(self, *args, **kwargs):
        self.dynamic_fields = kwargs.pop('fields', None)
        self.dynamic_exclude = kwargs.pop('exclude', None)
        error_message = (
            "You can't enable 'fields' AND 'exclude' at the same time"
        )

        if self.dynamic_fields and self.dynamic_exclude:
            raise Exception(error_message)

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        fields, exclude = self.get_dynamic_fields()

        if fields and exclude:
            raise Exception(error_message)

        if fields is not None:
            field_names = self.get_dynamic_field_names(fields)

            subset = set(field_names)
            existing = set(self.fields.keys())
            for field_name in existing - subset:
                self.fields.pop(field_name, None)

            self.distribute_fields(fields, field_names)

        elif exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)

    def get_from_profile(self):
        profile = self.context['request'].query_params['profile']
        return self.Meta.profiles[profile], tuple()

    def get_from_structure(self):
        return json.loads(
            self.context['request'].query_params['structure']
        ), None

    def get_from_context(self):
        return self.context.pop('fields'), self.context.pop('exclude')

    def get_dynamic_field_names(self, fields):
        return [
            field_entry.keys()[0]
            if isinstance(field_entry, dict)
            else field_entry

            for field_entry in fields
        ]

    def get_dynamic_fields(self):
        try:
            return self.get_from_structure()
        except (KeyError, ValueError):
            pass

        try:
            return self.get_from_profile()
        except (KeyError, AttributeError):
            pass

        try:
            return self.get_from_context()
        except KeyError:
            pass

        return self.dynamic_fields, self.dynamic_exclude

    def distribute_fields(self, fields, field_names):
        inherit = ('instance', 'data', 'partial', 'context',  # 'many',
                   'read_only', 'write_only', 'required', 'default',
                   'source', 'initial', 'label', 'help_text', 'style',
                   'error_messages', 'validators', 'allow_null')

        current_fields = set(self.fields.keys())
        for field_name, field_entry in zip(field_names, fields):
            if field_name not in current_fields:
                continue

            if not isinstance(field_entry, dict):
                continue

            field = self.fields[field_name]
            many = isinstance(field, serializers.ListSerializer)
            field = field.child if many else field

            if not isinstance(field, DynamicFieldsMixin):
                continue

            old_data = {
                attribute_name: getattr(field, attribute_name)
                for attribute_name in inherit
            }

            if old_data['source'] in ['', field_name]:
                old_data.pop('source')

            self.fields[field_name] = field.__class__(
                many=many,
                fields=field_entry[field_name],
                **old_data)
