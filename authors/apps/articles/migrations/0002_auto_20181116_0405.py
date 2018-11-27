# Generated by Django 2.1.2 on 2018-11-16 04:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('profiles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='tag_list',
            field=taggit.managers.TaggableManager(
                help_text='A comma-separated list of tags.',
                through='taggit.TaggedItem', to='taggit.Tag',
                verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='article',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='articles.Article'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='article',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='articles.Article'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_author',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='profiles.Profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='favoritearticle',
            name='article',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='articles.Article'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='favoritearticle',
            name='user',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likearticle',
            name='article',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                 to='articles.Article'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likearticle',
            name='user',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likecomment',
            name='comment',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='articles.Comment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likecomment',
            name='user',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rating',
            name='article',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='articles.Article'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rating',
            name='reader',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reportarticle',
            name='article',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='articles.Article'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reportarticle',
            name='user',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thread',
            name='thread_author',
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE,
                to='profiles.Profile'),
            preserve_default=False,
        ),
    ]