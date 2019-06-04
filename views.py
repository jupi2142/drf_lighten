import json


class DynamicStructureMixin(object):
    def get_serializer(self, *args, **kwargs):
        try:
            structure = self.request.query_params['structure']
            kwargs['fields'] = json.loads(structure)
        except (KeyError, ValueError, TypeError):
            pass
        return super(DynamicStructureMixin, self).get_serializer(*args,
                                                                 **kwargs)
