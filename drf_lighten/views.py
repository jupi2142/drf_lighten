import json

from django.conf import settings


class DynamicFieldsMixin(object):
    def get_serializer(self, *args, **kwargs):
        setting_names = ('DRF_LIGHTEN_INCLUDE', 'DRF_LIGHTEN_EXCLUDE')
        defaults = ('fields', 'exclude')
        argument_names = ('fields', 'exclude')

        bundle = zip(setting_names, defaults, argument_names)

        for setting_name, default, argument_name in bundle:
            try:
                query_param = getattr(settings, setting_name, default)
                structure = self.request.query_params[query_param]
                kwargs[argument_name] = json.loads(structure)
            except (KeyError, ValueError, TypeError):
                pass

        return super(DynamicFieldsMixin, self).get_serializer(*args, **kwargs)
