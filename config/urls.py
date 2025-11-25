"""
URL configuration for richardnixon.dev platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from apps.blog.sitemaps import BlogSitemap
from apps.portfolio.sitemaps import PortfolioSitemap

sitemaps = {
    'blog': BlogSitemap,
    'portfolio': PortfolioSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.blog.urls')),
    path('portfolio/', include('apps.portfolio.urls')),
    path('dashboards/', include('apps.dashboards.urls')),
    path('contact/', include('apps.contact.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
