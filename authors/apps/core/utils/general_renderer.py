import json
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList


class GeneralRenderer(JSONRenderer):
    def render(self, data,  media_type=None, renderer_context=None):
        if type(data) != ReturnList:
            errors = data.get('results', None)
            if errors is not None:
                return super().render(data)
            else:
                return json.dumps({
                    self.object_name: data
                })
        else:
            return json.dumps({
                self.object_name: data,
            })
