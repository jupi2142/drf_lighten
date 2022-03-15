from django.conf import settings


class Setting:
    def __init__(
        self,
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
        self.include = include
        self.exclude = exclude
        self.expansion = expansion
