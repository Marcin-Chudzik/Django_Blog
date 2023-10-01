from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'


class TagConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taggit'
