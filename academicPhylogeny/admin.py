# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin, messages
from academicPhylogeny.models import *
from ajax_select import make_ajax_form
import json

# Register your models here.

class UserContactAdmin(admin.ModelAdmin):
    search_fields = ["last_name","first_name","message", "email"]
    list_display = ["last_name","first_name","date_sent",'dealt_with']

class PhDAdmin(admin.ModelAdmin):
    search_fields = ["lastName","firstName","id"]
    list_filter = ["school", "validated"]
    list_editable = ["validated"]
    list_display = ["id",'__unicode__',"year", "school", "validated","submitter_email","source_of_info"]
    form = make_ajax_form(PhD, {
        'advisor': 'PhD',  # ManyToManyField
        'school': 'school',  # ForeignKeyField
        'specialization': 'specialization'
    })
class SchoolAdmin(admin.ModelAdmin):
    search_fields = ["name",]
    list_display = ["id","name"]


class FAQadmin(admin.ModelAdmin):
    list_display = ("heading","published","displayOrder")
    list_filter = ("published",)
    list_editable = ("published","displayOrder")

class UserProfilePictureAdmin(admin.ModelAdmin):
    list_display = ("photo", "associated_UserProfile")

# def updatePhDObject(modeladmin, request, queryset):
#     for obj in queryset:
#         dict = json.loads(obj.suggested_update_fixture)
#         PhD_obj = PhD.objects.get(pk=dict["id"])
#         PhD_obj.firstName = dict["firstName"]
#         PhD_obj.lastName = dict["lastName"]
#         PhD_obj.year = dict["year"]
#         PhD_obj.school = school.objects.get(pk=dict["school"])
#
#         PhD_obj.specialization.clear()
#         for special in dict["specialization"]:
#             PhD_obj.specialization.add(special)
#
#         PhD_obj.advisor.clear()
#         for advisor in dict["advisor"]:
#             PhD_obj.advisor.add(advisor)
#
#         PhD_obj.save()
#         messages.add_message(request, messages.INFO, "%s has been updated successfully" % (PhD_obj.__unicode__()))
#         obj.moderator_approved = True
#         obj.approver = request.user
#         obj.save()

class PhDUpdateAdmin(admin.ModelAdmin):
    list_display = ("date_sent","moderator_approved", "submitter_user", "source_of_info")
    #actions= [updatePhDObject]
    #this action is much better done using the /validate/ url which hits ValidateView

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id","user_email","associated_PhD","moderator_approved", "current_position","current_affiliation","research_website")
    list_editable = ("moderator_approved",)
    search_fields = ("user__email","associated_PhD__firstName","associated_PhD__lastName")

class SocialMediaPostsAdmin(admin.ModelAdmin):
    list_display = ("PhD", "date_posted", "facebook", "twitter")

class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

class LegacyPictureAdmin(admin.ModelAdmin):
    form = make_ajax_form(LegacyPicture,
                          {'associated_PhD':'PhD'}
                          )

admin.site.register(frequently_asked_question,FAQadmin)
admin.site.register(school, SchoolAdmin)
#admin.site.register(person, admin.ModelAdmin)
admin.site.register(PhD, PhDAdmin)
admin.site.register(userContact, UserContactAdmin)
admin.site.register(PhDupdate, PhDUpdateAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(socialMediaPosts, SocialMediaPostsAdmin)
admin.site.register(specialization, SpecializationAdmin)
admin.site.register(UserProfilePicture, UserProfilePictureAdmin)
admin.site.register(LegacyPicture, LegacyPictureAdmin)
