# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import reverse
from django.db import models
from django.contrib.auth.models import User
import json
from django.core.mail import send_mail, EmailMessage
from secrets import MAILCHIMP_API_KEY
import requests
import re
from datetime import datetime


class frequently_asked_question(models.Model):
    heading = models.CharField(max_length = 50)
    displayOrder = models.IntegerField()
    text = models.TextField(max_length = 2000,verbose_name ="HTML text")
    published = models.BooleanField(default=False)
    def __unicode__(self):
        return self.heading
    class Meta:
        ordering=["displayOrder"]
        verbose_name ="Frequently Asked Question"

class school(models.Model):
    name = models.CharField(max_length = 100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
            db_table = 'school'
            ordering = ['name']

class specialization(models.Model):
    name=models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

class PhD(models.Model):
    firstName = models.CharField(max_length=100,  null=True, verbose_name="First Name")
    lastName = models.CharField(max_length=100, null=True,  verbose_name="Last Name")
    year = models.IntegerField(max_length=4, blank=True, null=True, verbose_name="Year PhD Awarded")
    school = models.ForeignKey(school)
    advisor = models.ManyToManyField("self", null=True, blank=True, symmetrical=False)
    specialization = models.ManyToManyField(specialization, null=True, blank=True)
    URL_for_detail = models.CharField(max_length=200, null=True, blank=True)
    validated = models.NullBooleanField(default=False, blank=True)
    submitter_email = models.EmailField(verbose_name="Your Email Address")
    submitter_user = models.ForeignKey(User, null=True, blank=True, verbose_name="Submitter username")
    submitter_emailed_after_approval = models.BooleanField(default=False)
    source_of_info = models.CharField(max_length=300, verbose_name="What's the source of this info?")

    def __unicode__(self):
        name = self.firstName + " " + self.lastName
        return name

    def get_absolute_url(self):
        return reverse('PhD-detail-view', kwargs={'URL_for_detail': self.URL_for_detail})

    def save(self):  # custom save method for person to update detail URL
        #matches the charachters (, ), ', " to replace them below
        regex = r"\(|\)|\'|\""
        self.URL_for_detail = re.sub(regex,"", (self.firstName + "_" + self.lastName).replace(" ", "_"))
        if not self.pk: #only do this if object doesn't exist yet
            try:
                ob = self.submitter_user.userprofile
                profile = UserProfile.objects.get(pk=ob.id)
                profile.reputation_points = profile.reputation_points + 10
                profile.save()
            except:
                pass

        ## email submitter when this has been vaildated
        if self.validated and not self.submitter_emailed_after_approval:
            theEmail = EmailMessage(
                subject="Your submission to bioanthtree.org has been approved!",
                body="Hi there,\n\nThis is just a quick note to let you know your submission has been approved. You can see the new entry at this link - https://www.bioanthtree.org/detail/%s/\n\nThanks for contributing,\n\nThe team at bioanthtree.org" %(self.URL_for_detail,),
                from_email="admin@bioanthtree.org",
                to=[self.submitter_email],
                reply_to=["bioanthtree@gmail.com"]
            )
            theEmail.send()
            self.submitter_emailed_after_approval = True
        # call the normal PhD save method
        super(PhD, self).save()


    @property
    def network_edges_formatted(self):
        arrowSettings = {"from":{"scaleFactor":1.3}}
        edge_list = []

        for child in PhD.objects.filter(advisor=self, validated=True):
            for advisor in child.advisor.all():
                edge_list.append({"to":advisor.pk, "from":child.pk, "arrows":arrowSettings})

        for advisor in self.advisor.all():
            edge_list.append({"to":advisor.pk, "from":self.pk, "arrows":arrowSettings})
            for sibling in PhD.objects.filter(advisor=advisor,validated=True).exclude(pk=self.pk):
                edge_list.append({"to": advisor.pk, "from": sibling.pk, "arrows": arrowSettings})

        return json.dumps(edge_list)

    @property
    def network_nodes_formatted(self):
        selectedNodeColor = "#1e88e5"
        baseNodeColor = "#ffecb3"
        baseNodeColorHasNonVisibleAdvisees = "#ffca28"
        nodes = []
        node_ids = []

        nodes.append({"id": self.pk,
                      "label": " ".join((self.firstName, self.lastName)),
                      "color": selectedNodeColor,
                      "shape": "ellipse",
                      "font" : {"color":"white"},
                      "size": 20})
        node_ids.append(self.pk)
        advisors = self.advisor.all()
        for advisor in advisors:
            if PhD.objects.filter(advisor=advisor,validated=True).count() > 0:
                color = baseNodeColorHasNonVisibleAdvisees
            else:
                color = baseNodeColor
            if not advisor.pk in node_ids:
                nodes.append({"id": advisor.pk,
                              "label": " ".join((advisor.firstName, advisor.lastName)),
                              "color":color})
                node_ids.append(advisor.pk)
            for sibling in PhD.objects.filter(advisor=advisor, validated=True).exclude(pk=self.pk):
                if PhD.objects.filter(advisor=sibling, validated=True).count() > 0:
                    color = baseNodeColorHasNonVisibleAdvisees
                else:
                    color = baseNodeColor
                if not sibling.pk in node_ids:
                    nodes.append({"id": sibling.pk,
                                  "label": " ".join((sibling.firstName, sibling.lastName)),
                                  "color":color})
                    node_ids.append(sibling.pk)

        children = PhD.objects.filter(advisor=self, validated=True)
        for child in children:
            if PhD.objects.filter(advisor=child, validated=True).count() > 0:
                color = baseNodeColorHasNonVisibleAdvisees
            else:
                color = baseNodeColor
            if not child.pk in node_ids:
                nodes.append({"id": child.pk,
                              "label": " ".join((child.firstName, child.lastName)),
                              "color":color})
                node_ids.append(child.pk)

        return json.dumps(nodes)

    def find_children(self, descendants):
        ##pass an empty list when calling the first time
        for child in PhD.objects.filter(advisor=self, validated=True):
            descendants.append(child.__unicode__())
            child.find_children(descendants)
        return set(descendants)

    @property
    def find_root_ancestors(self):
        parents = []
        current_advisor = [advisor for advisor in self.advisor.all()]
        while current_advisor is not None:
            next_advisor = []
            for eachAdvisor in current_advisor:
                parents.append(eachAdvisor)
                for each in eachAdvisor.advisor.all():
                    next_advisor.append(each)
            if next_advisor:
                current_advisor = next_advisor
            else:
                current_advisor = None
        #get parents that are roots for their tree
        roots = []
        for parent in parents:
            if parent.advisor.all():
                pass
            else:
                roots.append(parent)
        return roots

    @property
    def get_nested_tree_dict(self):
        theDict = {}
        theDict["name"]=self.__unicode__()
        theDict["children"]=[]
        for each in PhD.objects.filter(advisor=self, validated=True):
            theDict["children"].append(each.get_nested_tree_dict)
        if len(theDict["children"])==0:
            del theDict["children"]
        return theDict

    @property
    def name_for_big_tree(self):
        return self.__unicode__().replace(".","")

    class Meta:
        db_table = 'PhD'
        unique_together = (("firstName", "lastName"),)
        ordering = ['lastName']
        verbose_name_plural = 'PhDs'
        verbose_name = "PhD"



class PhDupdate(models.Model):
    PhD = models.ForeignKey(PhD)
    moderator_approved = models.BooleanField(default=False)
    approver = models.ForeignKey(User, null=True, blank=True)
    suggested_update_fixture = models.TextField()
    submitter_email = models.EmailField(verbose_name="Your Email Address")
    submitter_user = models.ForeignKey(User, null=True, blank=True, related_name="submitter_user", verbose_name="Submitter username")
    source_of_info = models.CharField(max_length=300,verbose_name="What's the source of this info?")
    date_sent = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Suggested Update"
        verbose_name_plural = "Suggested Updates"

    def save(self):
        if not self.pk: #only do this next part if self is not already in DB
            try:
                profile = UserProfile.objects.get(pk=self.submitter_user.userprofile.id)
                profile.reputation_points = profile.reputation_points + 10
                profile.save()
            except AttributeError:
                pass
        if self.moderator_approved == True:
            try:
                theEmail = EmailMessage(
                    subject="Your suggested update to bioanthtree.org has been approved!",
                    body="Hi there,\n\nThis is just a quick note to let you know your suggested update has been approved. You can see the updated entry at this link - https://www.bioanthtree.org/detail/%s/\n\nThanks for contributing,\n\nThe team at bioanthtree.org" % (
                    self.PhD.URL_for_detail,),
                    from_email="admin@bioanthtree.org",
                    to=[self.submitter_email],
                    reply_to=["bioanthtree@gmail.com"]
                )
                theEmail.send()
            except:
                pass
        # call the normal save method
        super(PhDupdate, self).save()

class userContact(models.Model):
    email = models.EmailField(verbose_name="Your Email Address")
    first_name = models.CharField(max_length=100,verbose_name="Your First Name")
    last_name = models.CharField(max_length=100,verbose_name="Your Last Name")
    affiliation = models.CharField(max_length=100,verbose_name="Your Institutional Affiliation")
    message = models.TextField(max_length=2000,verbose_name="Your message")
    dealt_with = models.BooleanField(default=False)
    admin_notes = models.TextField(max_length=1000)
    date_sent = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('dealt_with','-date_sent')

    def __unicode__(self):
        display = "%s %s - (sent on %s)" % (self.first_name, self.last_name, self.date_sent.strftime("%Y-%m-%d")
)
        return display

    def save(self):
        ##only do it on the first save
        if not self.pk:
            theEmail = EmailMessage(
                subject="User contact on bioanthtree.org",
                body="On %s at %s %s wrote:\n\n%s" %(datetime.now().strftime("%h %d %Y"), datetime.now().strftime("%I:%M %p"), self.email, self.message),
                from_email="do-not-reply@bioanthtree.org",
                to=["bioanthtree@gmail.com"],
                reply_to=[self.email]
                )
            theEmail.send()
        super(userContact, self).save()


class UserProfile(models.Model):
    user = models.OneToOneField(to=User)
    moderator_approved = models.BooleanField(default=False)
    alert_email_sent = models.BooleanField(default=False)
    associated_PhD = models.OneToOneField(to=PhD)
    current_position = models.CharField(max_length=100, null=True, blank=True)
    current_affiliation = models.CharField(max_length=100, null=True, blank=True)
    reputation_points = models.IntegerField(default=10)
    research_website = models.URLField(null=True, blank=True)
    research_blurb = models.TextField(max_length=2000,verbose_name="Describe your research program (2000 characters max)", null=True, blank=True)

    def __unicode__(self):
        return "%s = %s" %(self.user, self.associated_PhD.firstName + " " + self.associated_PhD.lastName)

    def user_email(self):
        return self.user.email

    def save(self):
        #custom save method to send email when moderator has approved the user profile
        if self.moderator_approved:
            if not self.alert_email_sent:
                self.alert_email_sent = True
                auth = ("physphylo", MAILCHIMP_API_KEY)
                post_url = "https://us16.api.mailchimp.com/3.0/automations/c83a95694a/emails/9062c6526d/queue"
                data = {"email_address": self.user.email}
                r = requests.post(post_url, auth=auth, json=data)
                if r.status_code == 204:
                    pass
                else:
                    mess = "Trying to add %s to mailchimp automation queue post moderator admin of user profile\n" %(self.user.email,)
                    mess += r._content
                    send_mail(subject="physphylo error profile validation mailchimp email",
                              message=mess,
                              from_email="do-not-reply@bioanthtree.org",
                              recipient_list=("bioanthtree@gmail.com",))
        super(UserProfile, self).save()

class socialMediaPosts(models.Model):
    PhD = models.ForeignKey(PhD)
    date_posted = models.DateTimeField(auto_now_add=True)
    facebook = models.BooleanField(default=True)
    twitter = models.BooleanField(default=True)
    def __unicode__(self):
        return str(self.PhD) + " " + str(self.date_posted.date())
    class Meta:
        verbose_name_plural = "social media posts"
        verbose_name = "social media post"


def make_thumbnail(filename):
    from PIL import Image
    size = (1800, 1800)
    pic = Image.open(filename).convert("RGB")
    pic.thumbnail(size, Image.ANTIALIAS)
    pic.save(filename + ".THUMBNAIL", "JPEG")

class UserProfilePicture(models.Model):
    photo = models.ImageField()
    associated_UserProfile = models.OneToOneField(UserProfile)

    class Meta:
        verbose_name_plural = "User Profile Pictures"
        verbose_name = "User Profile Picture"

    def __unicode__(self):
            return self.associated_UserProfile.associated_PhD.firstName + " " + self.associated_UserProfile.associated_PhD.lastName

    def save(self):
        super(UserProfilePicture, self).save()
        make_thumbnail(self.photo.path)

class LegacyPicture(models.Model):
    #pictures uploaded by Admins, not by users
    photo = models.ImageField()
    associated_PhD = models.OneToOneField(PhD)


    def __unicode__(self):
        return self.associated_PhD.firstName + " " + self.associated_PhD.lastName


    def save(self):
        super(LegacyPicture, self).save()
        make_thumbnail(self.photo.path)


#######BELOW IS DEPRECATED###########
############################
CHOICES_editable_fields = [("firstName", "firstName"), ("lastName", "lastName"), ("year", "year")]

class suggestedPhDTextUpdate(models.Model):
    ## deals with user suggested updates for fields that can be stored as text
    PhD = models.ForeignKey(PhD)
    field = models.CharField(choices=CHOICES_editable_fields, max_length=100)
    value = models.CharField(max_length=100)
    moderator_approved = models.BooleanField(default=False)
    approver = models.ForeignKey(User, default=1)

class person(models.Model):
    firstName = models.CharField(max_length = 100,blank=True,null=True)
    middleName = models.CharField(max_length = 100,blank=True,null=True)
    lastName = models.CharField(max_length = 100,blank=True,null=True)
    yearOfPhD = models.IntegerField(max_length= 4, blank=True,null=True)
    school = models.ForeignKey(school)
    specialization = models.ManyToManyField(specialization,null=True,blank=True)
    URL_for_detail = models.CharField(max_length = 200,null=True)
    #shareImageURL = models.URLField(max_length=200, null=True, blank=True)
    featureImage = models.FileField(max_length=255, blank=True, upload_to="people/images/", null=True)
    featureBlurb = models.TextField(max_length=2000, null=True, blank=True, help_text="formatted with with <\p> tags")
    isFeatured = models.NullBooleanField()
    dateFeatured = models.DateField(null=True, blank=True)
    def get_absolute_url(self):
        return reverse('academicPhylogeny.views.detail', args=[self.URL_for_detail])

    def __unicode__(self):
            name = self.firstName + " " + self.lastName
            return name

    def save(self):#custom save method for person to update detail URL
        self.URL_for_detail = (self.firstName + "_" + self.lastName).replace(" ","_")

        #call the normal person save method
        super(person, self).save()

    class Meta:
            db_table = 'person'
            unique_together = (("firstName", "lastName"),)
            ordering = ['lastName']
            verbose_name_plural = 'people'



class connection(models.Model):
    advisor = models.ManyToManyField(person,related_name="a+")
    student = models.ForeignKey(person)

    def student_First_Name(self):
        return(self.student.firstName)
    student_First_Name.admin_order_field = 'student__firstName'

    def student_Last_Name(self):
        return(unicode(self.student.lastName))
    student_Last_Name.admin_order_field = 'student__lastName'

    def student_Year_Of_PhD(self):
        return(str(self.student.yearOfPhD))
    student_Year_Of_PhD.admin_order_field = 'student__yearOfPhD'

    def advisor_name(self):
        allAdvisors = []
        for each in self.advisor.all():
            allAdvisors.append(unicode(each.lastName))

        advisorNames = "/".join(allAdvisors)
        return(unicode(advisorNames))
    advisor_name.admin_order_field = 'advisor__lastName'

    def connectionJSON(self):
        allAdvisors = []
        try:
            for each in self.advisor.all():
                allAdvisors.append(unicode(each.firstName) + " " +  unicode(each.lastName))
            to_be_formatted = '{"source":"' + allAdvisors[0] + '", "target":"' + unicode(self.student.firstName) + " " + unicode(self.student.lastName) + '"}'
        except IndexError:
            to_be_formatted = '{"source":"' + "Unknown" + '", "target":"' + unicode(self.student.firstName) + " " + unicode(self.student.lastName) + '"}'
        return to_be_formatted.replace("None","Unknown")
    def __unicode__(self):
        return self.advisor_name() + "-->>" + self.student.firstName + " " + self.student.lastName + " (" + str(self.student.yearOfPhD) + ")"

    class Meta:
        db_table = "connection"
        unique_together = ('student',)
        ordering = ('student',)
#######ABOVE IS DEPRECATED###########
############################
