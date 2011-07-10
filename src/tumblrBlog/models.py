'''
Created on Jul 7, 2011

@author: aj
'''
from django.db import models

class Post(models.Model):    
    post_id = models.IntegerField()
    pub_date = models.DateTimeField('Publication date')
    title = models.CharField(max_length=255)
    content = models.TextField()
    content_src = models.URLField('Content source')
    tumblr_url = models.URLField('Permalink')
    
    def latest(self):
        return Post.objects.all().order_by('-pub_date')[:10] or []


class Tag(models.Model):
    tag_id = models.IntegerField()
    post_id = models.ForeignKey(Post)
    tag = models.CharField(max_length=255)
    
    

