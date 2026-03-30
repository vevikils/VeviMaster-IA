from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'mastering:landing',
            'mastering:studio',
            'mastering:converter',
            'analyzer:index',
            'mastering:about',
            'mastering:contact',
            'mastering:plans',
        ]

    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return [
            'mastering:blog_index',
            'mastering:blog_post_ai',
            'mastering:blog_post_prepare',
            'mastering:blog_post_diff',
            'mastering:blog_trap_fl_studio',
            'mastering:blog_masterizar_reggaeton',
            'mastering:blog_lufs_spotify',
            'mastering:blog_plugins_mastering',
            'mastering:blog_imagen_estereo',
            'mastering:blog_mastering_ia_vs_ingeniero',
        ]

    def location(self, item):
        return reverse(item)
