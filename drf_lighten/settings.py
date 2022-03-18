from django.conf import settings


class Setting:
    def __init__(
        self,
        structure: str = getattr(
            settings,
            "DRF_LIGTHEN_STRUCTURE",
            "struct",
        ),
        include: str = getattr(
            settings,
            "DRF_LIGTHEN_INCLUDE",
            "fields",
        ),
        exclude: str = getattr(
            settings,
            "DRF_LIGTHEN_EXCLUDE",
            "exclude",
        ),
        expansion: str = getattr(
            settings,
            "DRF_LIGTHEN_EXPANSION_CONFIG",
            "expandable_fields",
        ),
    ):
        self.struct = structure
        self.include = include
        self.exclude = exclude
        self.expansion = expansion
