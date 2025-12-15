from django.contrib.sitemaps import Sitemap
from .models import BlogPost


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(
            status=BlogPost.Status.PUBLISHED,
            is_private=False
        )

    def lastmod(self, obj):
        return obj.updated_at
