import operator

from rest_framework import serializers


class DynamicFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        if fields:
            self.lighten(fields, "fields")
        elif exclude:
            self.lighten(exclude, "exclude")

    def lighten(self, entries, argument):
        if argument == "fields":
            field_selector = operator.sub
        else:
            field_selector = operator.and_

        field_strings, field_dictionary = self.split_fields(entries)

        for field_name, field_entry in field_dictionary.items():
            if field_name in self.fields:
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

    def get_kwargs(self, field):
        field_name = field.field_name
        inherit = set(serializers.MANY_RELATION_KWARGS).union(
            set(serializers.LIST_SERIALIZER_KWARGS)
        )  # .union({'queryset', 'view_name'})

        kwargs = {}
        for attribute_name in inherit:
            value = getattr(field, attribute_name, None)
            if value is not None:
                kwargs[attribute_name] = value

        if kwargs["source"] in ["", field_name]:
            kwargs.pop("source")

        kwargs["context"] = kwargs.get("context") or self.context
        return kwargs

    def get_field_and_kwargs(self, field_name):
        field = self.fields[field_name]
        many = True
        if isinstance(field, serializers.ListSerializer):
            field = field.child
        elif isinstance(field, serializers.ManyRelatedField):
            field.child_relation.source = field.source
            field.child_relation.source_attrs = field.source_attrs
            field.child_relation.field_name = field.field_name
            field = field.child_relation
        else:
            many = False

        kwargs = self.get_kwargs(field)
        kwargs["many"] = many

        return field, kwargs

    def get_expanding_serializer(self, field, **kwargs):
        field_name = field.field_name
        expandable_fields = getattr(self.Meta, "expandable_fields", {})
        try:
            class_, exp_args, exp_kwargs = expandable_fields[field_name]
        except (ValueError, TypeError):
            class_, exp_args, exp_kwargs = expandable_fields[field_name], (), {}
        except KeyError:
            return field
        exp_kwargs.update(kwargs)
        return class_(*exp_args, **exp_kwargs)

    def pass_down_structure(self, field_name, field_entry, arg_name):
        field, kwargs = self.get_field_and_kwargs(field_name)
        kwargs[arg_name] = field_entry
        if not hasattr(field, "fields"):
            new_field = self.get_expanding_serializer(field, **kwargs)
        else:
            new_field = field.__class__(**kwargs)

        if getattr(new_field, "source"):
            return
        self.fields[field_name] = new_field
