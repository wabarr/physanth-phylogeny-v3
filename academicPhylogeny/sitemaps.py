from django.contrib.sitemaps import Sitemap
from academicPhylogeny.models import PhD

class PhDSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return PhD.objects.filter(validated=True)

    def location(self, obj):
        return "/detail/" + obj.URL_for_detail
