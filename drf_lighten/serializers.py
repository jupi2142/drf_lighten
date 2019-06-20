import operator

from django.utils.translation import ugettext


class DynamicFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)

        if fields and exclude:
            raise Exception(
                ugettext(
                    "You can't enable 'fields' AND 'exclude' at the same time"
                )
            )

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
        many = getattr(field, "many", False)
        field = getattr(field, "child", field)

        inherit = (
            "instance",
            "data",
            "partial",
            "context",
            "read_only",
            "write_only",
            "required",
            "default",
            "source",
            "initial",
            "label",
            "help_text",
            "style",
            "error_messages",
            "validators",
            "allow_null",
        )
        kwargs = {
            attribute_name: getattr(field, attribute_name, None)
            for attribute_name in inherit
        }
        kwargs["many"] = many

        if kwargs["source"] in ["", field_name]:
            kwargs.pop("source")

        kwargs['context'] = kwargs['context'] or self.context

        return field, kwargs

    def get_expanding_serializer(self, field, **kwargs):
        field_name = field.field_name
        expandable_fields = getattr(self.Meta, "expandable_fields", None)
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
        self.fields[field_name] = new_field
