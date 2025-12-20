from django.contrib.sitemaps import Sitemap
from .models import Project


class PortfolioSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Project.objects.filter(status=Project.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_at
