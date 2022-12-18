from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post

# Creating subclass of "Feed" class.
class LatestPostsFeed(Feed):
    # Attributes to match with elements of RSS channel.
    title = 'My Blog'
    link = '/blog/'
    description = 'New posts on my blog.'

    # Returns queryset of 5 the newest objects which are to be in channel message.
    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    # Returns description to item built from 30 first chars of its body.
    def item_description(self, item):
        return truncatewords(item.body, 30)
