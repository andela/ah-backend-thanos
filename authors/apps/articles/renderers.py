import json
from rest_framework.renderers import JSONRenderer
from .models import Article
from rest_framework.utils.serializer_helpers import ReturnList

from ..core.utils.generate_renderer import GeneralRenderer


class ArticleRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        '''
        Return a dictionary with 2 entries:
        key = "articles", value = a LIST of articles
        key = "articlesCount", value = number of articles
        '''
        if type(data) != ReturnList:
            errors = data.get('errors', None)
            if errors is not None:
                return super().render(data)
            else:
                return json.dumps({
                    'article': data
                })
        else:
            return json.dumps({
                'articles': data,
                'articlesCount': len(Article.objects.all())
            })


class CommentRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'comments'


class ThreadRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'threads'


class LikeStatusRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'Like_status'
    
class RatingRenderer(JSONRenderer):

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps({
            "article_scores": data,
        })
