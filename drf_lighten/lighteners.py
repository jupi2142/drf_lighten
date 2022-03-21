from abc import ABC, abstractmethod
from typing import Dict, List

from rest_framework.serializers import Serializer

from .types import Structure


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


def adapt(fields: Structure, type_="keep") -> dict:
    self_ = []
    nested = {}

    for field in fields:
        if isinstance(field, str):
            self_.append(field)
        elif isinstance(field, dict):
            for key, inner_field in field.items():
                nested[key] = adapt(inner_field, type_)

    return {
        "type": type_,
        "fields": {
            "self": self_,
            "nested": nested,
        },
    }


def merge(fields: dict, exclude: dict) -> dict:
    unified = {
        "type": "keep",
        "fields": {
            "self": [],
            "nested": {},
        },
    }
    if fields["fields"]["self"] and not exclude["fields"]["self"]:
        unified["type"] = "keep"
        unified["fields"]["self"] = fields["fields"]["self"]
    elif not fields["fields"]["self"] and exclude["fields"]["self"]:
        unified["type"] = "omit"
        unified["fields"]["self"] = exclude["fields"]["self"]

    all_nested_keys = list(fields["fields"]["nested"].keys()) + list(
        exclude["fields"]["nested"].keys()
    )

    for key in all_nested_keys:
        if (
            key in fields["fields"]["nested"]
            and key in exclude["fields"]["nested"]
        ):
            unified["fields"]["nested"][key] = merge(
                fields["fields"]["nested"][key],
                exclude["fields"]["nested"][key],
            )
        elif key in fields["fields"]["nested"]:
            unified["fields"]["nested"][key] = fields["fields"]["nested"][key]
        elif key in exclude["fields"]["nested"]:
            unified["fields"]["nested"][key] = exclude["fields"]["nested"][key]

    return unified
