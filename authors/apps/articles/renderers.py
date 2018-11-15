import json
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList

from authors.apps.core.utils.general_renderer import GeneralRenderer


class ArticleRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        '''
        Return a dictionary with 2 entries:
        key = "articles", value = a LIST of articles
        ke y = "articlesCount", value = number of articles
        '''
        response = renderer_context['response']
        if type(data) != ReturnList:
            errors = data.get('results', None)
            if errors is not None:
                return super().render(data)
            else:
                return json.dumps({
                    'status_code': response.status_code,
                    'results': data
                })
        else:
            return json.dumps({
                'status_code': response.status_code,
                'results': data,
                'articlesCount': len(data)
            })


class CommentRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'results'


class ThreadRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'results'


class LikeStatusRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'results'


class RatingRenderer(JSONRenderer):

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        response = renderer_context['response']
        return json.dumps({
            'status_code': response.status_code,
            "results": data,
        })


class BookmarkRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'results'


class FavoriteStatusRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'results'


class ReportArticleRenderer(JSONRenderer):
    charset = 'utf-8'
    object_name = 'results'

