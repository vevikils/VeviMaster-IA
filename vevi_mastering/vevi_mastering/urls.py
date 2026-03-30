"""
URL configuration for vevi_mastering project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mastering import views as mastering_views

from django.http import HttpResponse

def ads_txt(request):
    return HttpResponse("google.com, pub-2222481033433542, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def robots_txt(request):
    return HttpResponse("User-agent: *\nDisallow: /admin/\nDisallow: /accounts/\nAllow: /\nSitemap: https://www.vevimaster.com/sitemap.xml", content_type="text/plain")

from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, BlogSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
}
urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/mastering/favicon.svg')),
    path('googleaa24cee6c0f3f29f.html', lambda r: HttpResponse("google-site-verification: googleaa24cee6c0f3f29f.html", content_type="text/html")),
    path('accounts/', include('allauth.urls')),
    path('debug/media/', mastering_views.debug_media_files, name='debug_media'),
    path('ads.txt', ads_txt),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include('mastering.urls')),
    path('analyzer/', include('analyzer.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
