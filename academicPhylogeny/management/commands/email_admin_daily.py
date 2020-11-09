from django.core.management.base import BaseCommand
from academicPhylogeny.models import PhD, UserProfile, PhDupdate
from django.core.mail import send_mail
import json

class Command(BaseCommand):
    help = 'emails Admin with update on new submissions'

    def handle(self, *args, **options):
        submissionsToDo = PhD.objects.filter(validated=False)
        unvalidatedProfiles = UserProfile.objects.filter(moderator_approved=False)
        unvalidatedSuggestions = PhDupdate.objects.filter(moderator_approved=False)
        message=""
        if submissionsToDo.count() > 0:
            message += "There are %(submissionCount)s new submissions.\n"%{"submissionCount": submissionsToDo.count()}
            message += "http://www.bioanthtree.org/admin/academicPhylogeny/phd/?o=6.3\n\n"
        else:
            pass

        if unvalidatedProfiles.count() > 0:
            message += "\nThere are %(profilecount)s unvalidated profiles.\n"%{"profilecount": unvalidatedProfiles.count()}
            message += "http://www.bioanthtree.org/admin/academicPhylogeny/userprofile/\n\n"
        else:
            pass

        for sugg in unvalidatedSuggestions:
            try:
                json.loads(sugg.suggested_update_fixture)
                # automatically delete any that don't have valid JSON
                # since the suggest update template creates valid JSON,
                # this will weed out spam...little risky maybe since they are gone forever
            except ValueError:
                sugg.delete()
        unvalidatedSuggestions.update() #update queryset to get accurate count
        if unvalidatedSuggestions.count() > 0:
            message += "\nThere are %(suggestioncount)s unvalidated suggested changes.\n" % {
                "suggestioncount": unvalidatedSuggestions.count()}
            message += "http://www.bioanthtree.org/validate/\n\n"

        else:
            pass

        if message == "":
            pass
        else:
            send_mail("Submissions report bioanthtree.org", message, "do-not-reply@bioanthtree.org",
                  ["bioanthtree@gmail.com"], fail_silently=False)
