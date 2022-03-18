from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from rest_framework.serializers import Serializer

from .types import DictField, Structure


class LightenerABC(ABC):
    @abstractmethod
    def lighten(
        self,
        serializer: Serializer,
        structure: Dict[str, Dict],
    ) -> None:
        ...


class Lightener(LightenerABC):
    def _omit(self, serializer: Serializer, fields: List[str]):
        for field in fields:
            serializer.fields.pop(field, None)

    def _keep(self, serializer: Serializer, fields: List[str]):
        for field in list(serializer.fields.keys()):
            if field not in fields:
                serializer.fields.pop(field, None)

    def lighten(
        self,
        serializer: Serializer,
        structure: Dict[str, Dict],
    ) -> None:
        serializer = getattr(serializer, "child", serializer)
        if not hasattr(serializer, "fields"):
            return

        if structure["type"] == "omit":
            self._omit(serializer, structure["fields"]["self"])
        else:
            self._keep(
                serializer,
                (
                    structure["fields"].get("self", [])
                    + list(structure["fields"].get("nested", {}).keys())
                ),
            )

        for key, nested_structure in structure["fields"]["nested"].items():
            try:
                nested_serializer = serializer.fields[key]
            except KeyError:
                continue
            self.lighten(nested_serializer, nested_structure)



def convert(fields: Structure, type_='keep') -> dict:
    self_ = []
    nested = {}

    if not fields:
        return {} 

    for field in fields:
        if isinstance(field, str):
            self_.append(field)
        elif isinstance(field, dict):
            for key, inner_field in field.items():
                nested[key] = convert(inner_field, type_)

    return {
        "type": type_,
        "fields": {
            "self": self_,
            "nested": nested
        }
    }


def merge(field_structure, exclude_structure) -> dict:
    ...

def structure_adapter(
    fields: Optional[Structure] = None,
    exclude: Optional[Structure] = None,
) -> dict:
    field_structure = convert(fields or [], 'keep')
    exclude_structure = convert(exclude or [], 'omit')
    
    return merge(field_structure, exclude_structure)
