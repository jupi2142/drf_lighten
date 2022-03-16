from abc import ABC, abstractmethod
from typing import List, Tuple

from rest_framework import serializers

from .types import DictField, Structure


class Lightener(ABC):
    def get_fields(self, structure: Structure) -> Tuple[List[str], DictField]:
        current, nested = [], {}
        for field in structure:
            if isinstance(field, str):
                current.append(field)
            elif isinstance(field, dict):
                nested.update(field)
        return current, nested

    @abstractmethod
    def fields_to_keep(
        self,
        serializer: serializers.Serializer,
        current: List[str],
        nested: DictField,
    ) -> List[str]:
        ...

    def lighten(
        self,
        serializer: serializers.Serializer,
        structure: Structure,
    ) -> None:
        serializer = getattr(serializer, "child", serializer)
        if not hasattr(serializer, "fields"):
            return

        current, nested = self.get_fields(structure)
        keep = self.fields_to_keep(serializer, current, nested)

        serializer.fields = {
            field_name: field
            for field_name, field in serializer.fields.items()
            if field_name in keep
        }

        for key, structure in nested.items():
            try:
                nested_serializer = serializer.fields[key]
            except KeyError:
                continue
            self.lighten(nested_serializer, structure)


class Keeper(Lightener):
    def fields_to_keep(
        self,
        serializer: serializers.Serializer,
        current: List[str],
        nested: DictField,
    ) -> List[str]:
        if "*" in current:
            return list(serializer.fields.keys())
        return current + list(nested.keys())


class Omitter(Lightener):
    def fields_to_keep(
        self,
        serializer: serializers.Serializer,
        current: List[str],
        nested: DictField,
    ) -> List[str]:
        if "*" in current:
            current = list(serializer.fields.keys())
        return list(set(serializer.fields.keys()) - set(current)) + list(
            nested.keys()
        )
