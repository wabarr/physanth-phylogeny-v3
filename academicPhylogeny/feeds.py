from django.contrib.syndication.views import Feed
from academicPhylogeny.models import PhD

class PhDFeed(Feed):
    title = "PhD feed"
    link = "/feed/"
    description = "RSS listing of bioanth PhDs"

    def items(self):
        return PhD.objects.all()

    def item_title(self, item):
        return item

    def item_description(self, item):
        return "%s received a PhD from %s in %s." % (item, item.school, item.year)

    def item_link(self, item):
        return "https://www.bioanthtree.org/detail/%s" %(item.URL_for_detail,)