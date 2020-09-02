import operator

from django.conf import settings
from rest_framework import relations, serializers

from .parsers import split
from .utils import get_model_serializer_subclasses

try:
    string_type = basestring
except NameError:
    string_type = str


class DynamicFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        if fields is not None:
            self.lighten(fields, "fields")
        elif exclude is not None:
            self.lighten(exclude, "exclude")

    @classmethod
    def get_model_serializer(cls, model):
        subclasses = get_model_serializer_subclasses(cls)
        for subclass in subclasses:
            try:
                if subclass.Meta.model == model:
                    return subclass
            except AttributeError:
                pass

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
        strings, dictionary = split(fields)
        if strings == ["*"]:
            strings = set(self.fields.keys()) - set(dictionary.keys())
        return strings, dictionary

    def get_kwargs(self, field):
        field_name = field.field_name
        inherit = (
            set(relations.MANY_RELATION_KWARGS)
            .union(set(serializers.LIST_SERIALIZER_KWARGS))
            .difference({"html_cutoff_text", "html_cutoff"})
        )

        kwargs = {}
        for attribute_name in inherit:
            try:
                kwargs[attribute_name] = getattr(field, attribute_name)
            except AttributeError:
                pass

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
        expansion_dict_attribute = getattr(
            settings, "DRF_LIGHTEN_EXPANSION_CONFIG", "expandable_fields"
        )
        expansion_dict = getattr(self.Meta, expansion_dict_attribute, {})
        try:
            class_, exp_args, exp_kwargs = expansion_dict[field_name]
        except (ValueError, TypeError):
            class_, exp_args, exp_kwargs = expansion_dict[field_name], (), {}
        except KeyError:
            current_model = self.Meta.model
            model_field = current_model._meta.get_field(field.source)
            target_model = model_field.target_field.model
            try:
                class_ = DynamicFieldsMixin.get_model_serializer(target_model)
                if class_ is None:
                    raise ValueError
            except ValueError:
                try:
                    from drf_generator.serializers import serializer_factory
                except ImportError:
                    return field
                class_ = serializer_factory(target_model)
            exp_args, exp_kwargs = (), {}
        exp_kwargs.update(kwargs)
        return class_(*exp_args, **exp_kwargs)

    def pass_down_structure(self, field_name, field_entry, arg_name):
        field, kwargs = self.get_field_and_kwargs(field_name)
        kwargs[arg_name] = field_entry
        if not hasattr(field, "fields"):
            new_field = self.get_expanding_serializer(field, **kwargs)
        else:
            try:
                return field.lighten(field_entry, arg_name)
            except AttributeError:
                return

        if getattr(new_field, "source"):
            return
        self.fields[field_name] = new_field
