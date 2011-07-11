'''
Created on Jul 7, 2011

@author: aj
'''
from django.db import models
from tumblrBlog import tumblrPosts

class Post(models.Model):    
    post_id = models.IntegerField()
    date = models.DateTimeField('Publication date')
    regular_title = models.CharField('Title', max_length=255)
    slug = models.CharField(max_length=255)
    regular_body = models.TextField()
    tumblr_url = models.URLField('Permalink')
    type = models.CharField('Type', max_length=255)
    format = models.CharField(max_length=255)
    
    @classmethod
    def latest(self):
        Post.__retrieve
        return Post.objects.all().order_by('-date')[:10] or []
    
    @classmethod
    def __retrieve():
        latest_in_cache_time = Post.objects.all(order_by='-date')[0].date
        if tumblrPosts.check(latest_in_cache_time):
            [post.save() for post in tumblrPosts.get()]
            return True
        return False

class Tag(models.Model):
    tag_id = models.IntegerField()
    post_id = models.ForeignKey(Post)
    tag = models.CharField(max_length=255)
    
    
class Settings(models.Model):
    tumblr_account = models.CharField('Tumblr user address', max_length=255)
    last_retrieval_date = models.DateTimeField('Last retrieval')
    cache_time_to_live  = models.IntegerField('Cache time to live')
    account_name = models.CharField('Account name (optional)', max_length=255)
    

