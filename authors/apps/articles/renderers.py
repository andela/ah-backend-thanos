import json
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList

from ..core.utils.general_renderer import GeneralRenderer
from .models import Article


class ArticleRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        '''
        Return a dictionary with 2 entries:
        key = "articles", value = a LIST of articles
        ke y = "articlesCount", value = number of articles
        '''
        if type(data) != ReturnList:
            errors = data.get('results', None)
            if errors is not None:
                return super().render(data)
            else:
                return json.dumps(
                    data
                )
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


class BookmarkRenderer(GeneralRenderer):
    charset = 'utf-8'
    object_name = 'bookmark'


class FavoriteStatusRenderer(JSONRenderer):
    charset = 'utf-8'
    object_name = 'favorite_status'
