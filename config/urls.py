"""
URL configuration for richardnixon.dev platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequired

from apps.blog.sitemaps import BlogSitemap
from apps.portfolio.sitemaps import PortfolioSitemap

# Patch admin to require OTP
admin.site.__class__ = AdminSiteOTPRequired

sitemaps = {
    'blog': BlogSitemap,
    'portfolio': PortfolioSitemap,
}

# URLs that don't need language prefix
urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
