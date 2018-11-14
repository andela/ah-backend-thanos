import re
import time
from authors.apps.articles.models import Article


def generate_slug(title):
    # slug: Allow only alphanumeric values and dashes for spaces
    slug = ''
    for i in re.split(r'(.)', title.strip().lower()):
        if i.isalnum():
            slug += i
        elif i == ' ':
            slug += '-'
    if Article.objects.filter(slug=slug).exists():
        slug += str(time.time()).replace('.', '')
    return slug
