__author__ = 'Derek Stegelman'
__date__ = '9/5/12'

from django.db import models

from sprints.choices import STORY_STATUS
from base import AuditBase

class Roadblock(AuditBase):
    title = models.CharField(max_length=250, blank=False, null=True)
    story = models.ForeignKey(Story, null=True, blank=False)

class Story(AuditBase):
    title = models.CharField(max_length=250, blank=False, null=True)
    status = models.CharField(choices=STORY_STATUS, max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.title

class Sprint(AuditBase):
    name = models.CharField(max_length=250, blank=True, null=True)
    start_date = models.DateField(blank=False, null=True)
    end_date = models.DateField(blank=False, null=True)

    locked = models.BooleanField()

    def __unicode__(self):
        return None
