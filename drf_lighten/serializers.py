from typing import Dict, List, Optional

from .lighteners import Lightener, LightenerABC, structure_adapter
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


class DynamicFieldsMixin(DynamicStructureMixin):
    def __init__(
        self,
        *args,
        fields: Optional[Structure] = None,
        exclude: Optional[Structure] = None,
        **kwargs,
    ):

        structure = None
        if fields or exclude:
            structure = structure_adapter(fields, exclude)
        super(DynamicFieldsMixin, self).__init__(
            structure=structure,
            *args,
            **kwargs,
        )
