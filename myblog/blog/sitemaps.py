from django.contrib.sitemaps import Sitemap
from .models import Post

# Create a sitemap by inheriting from Sitemap class.
class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    # Returns queryset of objects which are to be in sitemap.
    def items(self):
        return Post.published.all()

    # Returns data and time of last modification for each object in queryset.
    def lastmod(self, obj):
        return obj.publish
