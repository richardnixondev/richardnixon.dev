"""
URL configuration for richardnixon.dev platform.
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequired

from apps.api.api import api
from apps.blog.sitemaps import BlogSitemap
from apps.core.views import health
from apps.portfolio.sitemaps import PortfolioSitemap

# Patch admin to require OTP
admin.site.__class__ = AdminSiteOTPRequired

sitemaps = {
    'blog': BlogSitemap,
    'portfolio': PortfolioSitemap,
}

# URLs that don't need language prefix
urlpatterns = [
    path('health/', health, name='health'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('api/', api.urls),
]

# URLs with language prefix (/pt-br/, /en/)
urlpatterns += i18n_patterns(
    path('', include(tf_urls)),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.blog.urls')),
    path('portfolio/', include('apps.portfolio.urls')),
    path('contact/', include('apps.contact.urls')),
    prefix_default_language=True,
)

# Serve media files in all environments (static() is empty when DEBUG=False)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
