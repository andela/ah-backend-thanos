from django_filters.rest_framework import FilterSet, filters
from .models import Article


class ArticlesFilter(FilterSet):
    title = filters.CharFilter(field_name='title', method='get_title')
    author = filters.CharFilter(field_name='author', method='get_author')
    tag = filters.CharFilter(field_name='tag', method='get_tags')

    def get_title(self, queryset, name, value):
        return queryset.filter(title__icontains=value)

    def get_author(self, queryset, name, value):
        return queryset.filter(author__username=value)

    def get_tags(self, queryset, name, value):
        return queryset.filter(tag_list__name__icontains=value)

    class Meta():
        model = Article
        fields = {'author', 'title', 'tag'}
