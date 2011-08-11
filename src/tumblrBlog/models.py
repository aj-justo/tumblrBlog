'''
Created on Jul 7, 2011

@author: aj
'''
from django.db import models

class Post(models.Model):    
    post_id = models.IntegerField()
    date = models.FloatField('Publication date')
    regular_title = models.CharField('Title', max_length=255)
    slug = models.CharField(max_length=255)
    regular_body = models.TextField()
    tumblr_url = models.URLField('Permalink')
    type = models.CharField('Type', max_length=255)
    format = models.CharField(max_length=255)
    
    @classmethod
    def latests(self, limit):
        return Post.objects.all().order_by('-date')[:limit] or []
    
       
        
    @classmethod
    def TumblrPostToCache(cls, post):
        cpost = Post()
        cpost.post_id = post['id']
        cpost.date = post['unix-timestamp']
        cpost.regular_title = post['regular-title']
        cpost.regular_body = post['regular-body']
        cpost.type = post['type']
        cpost.format = post['format']
        cpost.tumblr_url = post['url']
        cpost.slug = post['slug']
        cpost.save()
        
       

class Tag(models.Model):
    tag_id = models.IntegerField()
    post_id = models.ForeignKey(Post)
    tag = models.CharField(max_length=255)
    
    
class Settings(models.Model):
    tumblr_account = models.CharField('Tumblr user address', max_length=255)
    last_retrieval_date = models.DateTimeField('Last retrieval')
    cache_time_to_live  = models.IntegerField('Cache time to live')
    account_name = models.CharField('Account name (optional)', max_length=255)
    

