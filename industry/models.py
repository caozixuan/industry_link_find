from __future__ import unicode_literals

from django.db import models


class Industry(models.Model):
    name = models.CharField(max_length=100)
    upstream = models.CharField(max_length=100,null=True)
    downstream = models.CharField(max_length=100,null=True)


class Company(models.Model):
    name = models.CharField(max_length=100)
    up_link = models.ManyToManyField(Industry, null=True,related_name='up')
    down_link = models.ManyToManyField(Industry, null=True,related_name='down')
    mid_link = models.ManyToManyField(Industry, null=True,related_name='mid')


class Dictionary(models.Model):
    is_industry = models.BooleanField(default=False)
    name = models.CharField(max_length=100)

