from ajax_select import register, LookupChannel
from .models import school, PhD, specialization
from django.db.models import Value
from django.db.models.functions import Concat

@register('school')
class TagLookup(LookupChannel):

    model = school

    def get_query(self, q, request):
        return self.model.objects.filter(name__contains=q)

    def format_item_display(self, item):
        return u"<div class='chip blue darken-1 white-text'>%s</div>" % item.name

    def check_auth(self, request):
            return True

@register('PhD')
class PhDLookup(LookupChannel):

    model = PhD

    def check_auth(self, request):
            return True

    def get_query(self, q, request):
        queryset = PhD.objects.annotate(fullName=Concat('firstName',Value(' '),'lastName'))
        return queryset.filter(fullName__icontains=q)

    def format_item_display(self, item):
        return u"<div class='chip'>%s %s</div>" % (item.firstName, item.lastName)

@register('specialization')
class SpecializationLookup(LookupChannel):

    model = specialization

    def get_query(self, q, request):
        return self.model.objects.filter(name__contains=q)
    def check_auth(self, request):
            return True