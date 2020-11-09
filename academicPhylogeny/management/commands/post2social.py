# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from academicPhylogeny.models import PhD, socialMediaPosts
from academicPhylogeny.secrets import FACEBOOK_PHYSPHYLO_PAGE_ID,FACEBOOK_PHYSPHYLO_PAGE_ACCESS_TOKEN, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
import requests
import tweepy
import re
from datetime import date

class Command(BaseCommand):
    help = 'posts to facebook'

    def add_arguments(self, parser):

        parser.add_argument(
            '--showupcoming',
            action='store_true',
            dest='showupcoming',
            help='show queue of upcoming social media posts rather than posting any',
        )

    def debug(self, TWmsg, FBmsg):
        self.stdout.write("Tweet:" + TWmsg)
        self.stdout.write("\nFacebook:" + FBmsg)

    def showupcoming(self):
        prior_posts = socialMediaPosts.objects.all().values_list("PhD")
        unpostedCurrentYearPhDs = PhD.objects.filter(year=date.today().year, validated=True).exclude(id__in=prior_posts)
        DONOTPOST = [48, 638, 99, 90]
        legacyPhDs = PhD.objects.filter(validated=True, school__isnull=False, year__isnull=False,
                                        year__lte=2000).order_by("year").exclude(id__in=prior_posts).exclude(id__in=DONOTPOST)
        for each in legacyPhDs[0:99]:
            self.stdout.write(each.__unicode__())

    def post(self, selectedPhD, TWmsg=None, FBmsg=None, link=None):
        newPostDB = None
        # if FBmsg:
        #     token = FACEBOOK_PHYSPHYLO_PAGE_ACCESS_TOKEN
        #     pageID = FACEBOOK_PHYSPHYLO_PAGE_ID
        #     dataDict = {"message": FBmsg, "link": link, "access_token": token}
        #     post_url = "https://graph.facebook.com/v2.10/%d/feed" % (pageID,)
        #     r = requests.post(url=post_url, data=dataDict)
        #     if r.status_code == 200:
        #         self.stdout.write(self.style.SUCCESS('Successfully posted to facebook!'))
        #         if not newPostDB:
        #             newPostDB = socialMediaPosts(PhD=selectedPhD,facebook=True,twitter=False)
        #             newPostDB.save()
        #         else:
        #             newPostDB.facebook = True
        #             newPostDB.save()
        #     else:
        #        self.stdout.write(self.style.ERROR("Facebook post failure."))

        if TWmsg:
            auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth)

            ## all URLS are 23 characters, total max chars is 280
            if len(TWmsg) < 256:
                # need room for a space, then 23 character link, so max length for a single tweet is 256 (256 + 1 space + 23 char link = 280 chars)
                t = api.update_status(TWmsg + " " + link)
            else:
                # leave 10 characters for ... and the tweet number marker with a space in front e.g. ... (1/20)
                # first tweet is thus 107 chars max (link in first tweet)

                n = 246
                tweets = [''] 
                currentTweet = 0

                for word in re.findall(r'\S+', TWmsg):
                    proposed = " ".join([tweets[currentTweet], word]).lstrip()
                    if len(proposed) <= n:
                        tweets[currentTweet] = proposed
                    else:
                        tweets.append("")
                        currentTweet += 1
                        tweets[currentTweet] = " ".join([tweets[currentTweet], word]).lstrip()

                ## add ellipses
                for i in range(0, len(tweets) - 1):
                    tweets[i] = tweets[i] + "..."

                ## add link to first tweet
                tweets[0] = tweets[0] + " " + link

                ## add tweet number
                for i in range(0, len(tweets)):
                    tweets[i] = tweets[i] + " (%d/%d)" % (i + 1, len(tweets))

                for i in range(0, len(tweets)):
                    if i == 0:
                        # first tweet stands alone
                        t = api.update_status(tweets[i])
                    else:
                        # subsequent tweets are in reply to previous tweet
                        t = api.update_status(tweets[i], in_reply_to_status_id=t.id)

            if not newPostDB:
                newPostDB = socialMediaPosts(PhD=selectedPhD, facebook=False, twitter=True)
                newPostDB.save()
            else:
                newPostDB.twitter = True
                newPostDB.save()


    def handle(self, *args, **options):
        if options['showupcoming']:
            self.showupcoming()
        else:

            prior_posts = socialMediaPosts.objects.all().values_list("PhD")
            unpostedCurrentYearPhDs = PhD.objects.filter(year__in=[date.today().year,date.today().year - 1], validated=True).exclude(id__in=prior_posts)
            DONOTPOST = [48,638,99,90]
            legacyPhDs = PhD.objects.filter(validated=True, school__isnull=False, year__isnull=False, year__lte=2000).order_by("year").exclude(id__in=prior_posts).exclude(id__in=DONOTPOST)


            if unpostedCurrentYearPhDs.__len__() > 0:
                selectedPhD = unpostedCurrentYearPhDs[0]
                link = "https://www.bioanthtree.org%s" % (selectedPhD.get_absolute_url(),)
                FBmsg = ("Congratulations to Dr. %s, who recently completed a PhD at %s with %s."
                         " This information now appears in the academic genealogy network on our website!"
                         " Submit your own information if it isn't already in the database!") % (
                            selectedPhD.firstName + " " + selectedPhD.lastName,
                            selectedPhD.school,
                            (" and ").join(
                                [advisor.firstName + " " + advisor.lastName for advisor in selectedPhD.advisor.all()])
                        )

                TWmsg = "Congrats to Dr. %s for completing a PhD at %s with %s! #bioanthphd" % (
                    selectedPhD.firstName + " " + selectedPhD.lastName,
                    selectedPhD.school,
                    " and ".join([advisor.firstName + " " + advisor.lastName for advisor in selectedPhD.advisor.all()]).replace("  ", " ")
                )
            else:
                selectedPhD = legacyPhDs[0]
                link = "https://www.bioanthtree.org%s" % (selectedPhD.get_absolute_url(),)
                advisorPhrase = ""
                advisorPeriodOrNot = "."
                if(len(selectedPhD.advisor.all()) > 0):
                    advisorsAnd = (" and ").join(
                                [advisor.firstName + " " + advisor.lastName for advisor in selectedPhD.advisor.all()]
                    )
                    advisorPhrase = "with " + advisorsAnd + "."
                    advisorPeriodOrNot = ""
                studentsPhrase = ""
                students = PhD.objects.filter(validated=True, advisor = selectedPhD)
                if len(students) > 0:
                    if len(students) == 1:
                        plural_or_not=""
                    else:
                        plural_or_not="s"
                    studentsPhrase = "%s advised/has advised at least %d PhD student%s including: %s." %(
                        selectedPhD.lastName,
                        len(students),
                        plural_or_not,
                        ", ".join([student.__unicode__().strip() for student in students])
                    )
                total_descendant_count = len(selectedPhD.find_children([]))
                if total_descendant_count > 5 and total_descendant_count > len(students):
                    totalDescendantPhrase = "In total, %d PhDs in our database are academic descendants of %s." % (total_descendant_count, selectedPhD.lastName)
                else:
                    totalDescendantPhrase = ""

                FBmsg = TWmsg =  re.sub(" +"," ", "%s completed a PhD at %s in %s%s %s %s %s\n\nLearn more on our website..." % (
                            selectedPhD.__unicode__().strip(),
                            selectedPhD.school,
                            selectedPhD.year,
                            advisorPeriodOrNot,
                            advisorPhrase,
                            studentsPhrase,
                            totalDescendantPhrase
                        ))


            #self.debug(TWmsg, FBmsg)
            self.post(selectedPhD=selectedPhD, FBmsg=FBmsg, TWmsg=TWmsg, link=link)