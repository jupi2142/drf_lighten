from django.conf import settings

from .lighteners import Keeper, Lightener, Omitter

default_keeper = Keeper()
default_omitter = Omitter()


class DynamicFieldsMixin(object):
    def __init__(
        self,
        *args,
        keeper: Lightener = default_keeper,
        omitter: Lightener = default_omitter,
        **kwargs,
    ):
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        if fields is not None:
            keeper.lighten(self, fields)
        elif exclude is not None:
            omitter.lighten(self, exclude)
