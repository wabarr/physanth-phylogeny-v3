from django.core.management.base import BaseCommand
from academicPhylogeny.models import UserProfile
from academicPhylogeny.secrets import MAILCHIMP_API_KEY
import requests


class Command(BaseCommand):
    help = 'emails Admin with update on new submissions'

    def handle(self, *args, **options):
        auth = ("physphylo", MAILCHIMP_API_KEY)
        post_url = "https://us16.api.mailchimp.com/3.0/automations/6d00a4f491/emails/b3a93f0665/queue"

        unmodified_profiles = UserProfile.objects.filter(moderator_approved=True,
                                            current_position__isnull=True,
                                            current_affiliation__isnull=True,
                                            research_website__isnull=True,
                                            research_blurb__isnull=True)

        for profile in unmodified_profiles:
            data = {"email_address": profile.user.email}
            r = requests.post(post_url, auth=auth, json=data)
            if r.status_code == 204:
                self.stdout.write(self.style.SUCCESS('SUCCESS: email sent to ' + profile.user.email))
            else:
                self.stdout.write(self.style.ERROR("ERROR:" + str(r.status_code) + " " + profile.user.email))


