from django.db import models
from django.contrib.sites.models import Site

from allauth.socialaccount.defs import SocialAccountProvider
from allauth.socialaccount.models import SocialAccount


class FacebookAppManager(models.Manager):

    def get_current(self):
        """
        Get the FacebookApp corresponding to the current site.

        :returns: A :class:`FacebookApp` instance or ``None`` if no match is
            found.
        """
        site = Site.objects.get_current()
        try:
            return self.get(site=site)
        except FacebookApp.DoesNotExist:
            pass


class FacebookApp(models.Model):
    objects = FacebookAppManager()

    site = models.ForeignKey(Site)
    name = models.CharField(max_length=40)
    application_id = models.CharField(max_length=80)
    api_key = models.CharField(max_length=80)
    application_secret = models.CharField(max_length=80)

    def __unicode__(self):
        return u"%s (@%s)" % (self.name, self.site)


class FacebookAccount(SocialAccount):
    social_id = models.CharField(max_length=255, blank=False, unique=True)
    name = models.CharField(max_length=255)
    link = models.URLField()

    def get_profile_url(self):
        return self.link

    def get_provider(self):
        return SocialAccountProvider.FACEBOOK

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.social_id)
