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
    def lighten(
        self,
        serializer: serializers.Serializer,
        structure: Structure,
    ) -> None:
        ...


class Keeper(Lightener):
    def lighten(
        self,
        serializer: serializers.Serializer,
        structure: Structure,
    ) -> None:
        keep_current, keep_nested = self.get_fields(structure)

        keep = keep_current + list(keep_nested.keys())

        if "*" not in keep:
            if not hasattr(serializer, "fields"):
                serializer = serializer.child
                # expand if structure says nested
                # Replace serializers inside the lightener subclasses
                # Keeper if .child isn't working


            serializer.fields = {
                field_name: field
                for field_name, field in serializer.fields.items()
                if field_name in keep
            }

        for key, structure in keep_nested.items():
            try:
                nested_serializer = serializer.fields[key]
                self.lighten(nested_serializer, structure)
            except KeyError:
                continue


class Omitter(Lightener):
    def lighten(
        self,
        serializer: serializers.Serializer,
        structure: Structure,
    ) -> None:
        omit_current, omit_nested = self.get_fields(structure)

        if "*" not in omit_current:
            if not hasattr(serializer, "fields"):
                serializer = serializer.child
                # expand if structure says nested
                # Replace serializers inside the lightener subclasses
                # Keeper if .child isn't working

            serializer.fields = {
                field_name: field
                for field_name, field in serializer.fields.items()
                if field_name not in omit_current
            }

        for key, structure in omit_nested.items():
            try:
                nested_serializer = serializer.fields[key]
                self.lighten(nested_serializer, structure)
            except KeyError:
                continue
