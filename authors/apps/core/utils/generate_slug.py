import re


def generate_slug(title):
    # slug: Allow only alphanumeric values and dashes for spaces
    slug = ''
    for i in re.split(r'(.)', title.strip().lower()):
        if i.isalnum():
            slug += i
        elif i == ' ':
            slug += '-'
    return slug
