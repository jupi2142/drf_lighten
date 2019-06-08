import json
from django.conf import settings


class DynamicStructureMixin(object):
    def get_serializer(self, *args, **kwargs):
        try:
            query_param = getattr(settings, 'DRF_LIGHTEN_INCLUDE', 'fields')
            structure = self.request.query_params[query_param]
            kwargs['fields'] = json.loads(structure)
        except (KeyError, ValueError, TypeError):
            pass

        try:
            query_param = getattr(settings, 'DRF_LIGHTEN_EXCLUDE', 'exclude')
            structure = self.request.query_params[query_param]
            kwargs['exclude'] = json.loads(structure)
        except (KeyError, ValueError, TypeError):
            pass

        return super(DynamicStructureMixin, self).get_serializer(*args,
                                                                 **kwargs)
