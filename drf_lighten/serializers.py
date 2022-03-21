from typing import Optional

from .lighteners import Lightener, LightenerABC, adapt, merge
from .types import Structure


class DynamicStructureMixin(object):
    def __init__(
        self,
        *args,
        structure: Optional[dict] = None,
        lightener: LightenerABC = Lightener(),
        **kwargs,
    ):
        super(DynamicStructureMixin, self).__init__(*args, **kwargs)

        if structure:
            lightener.lighten(self, structure)


class DynamicFieldsMixin(object):
    def __init__(
        self,
        *args,
        fields: Optional[Structure] = None,
        exclude: Optional[Structure] = None,
        lightener: LightenerABC = Lightener(),
        **kwargs,
    ):
        super(DynamicFieldsMixin, self).__init__(
            *args,
            **kwargs,
        )

        if fields or exclude:
            lightener.lighten(
                self,
                merge(
                    adapt(fields or [], "keep"),
                    adapt(exclude or [], "omit"),
                ),
            )
