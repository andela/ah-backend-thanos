import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList


class GeneralRenderer(JSONRenderer):
    charset = 'utf-8'
    object_name = 'object'
    object_count = 'objectCount'

    def render(self, data, media_type=None, renderer_context=None):
        if type(data) != ReturnList:
            errors = data.get('errors', None)
            if errors is not None:
                return super().render(data)
            return json.dumps({
                self.object_name: data
            })
