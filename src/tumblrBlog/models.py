'''
Created on Jul 7, 2011

@author: aj
'''
from django.db import models
from util.tumblr import Api, TumblrError 
from tumblrBlog import settings
import datetime, hashlib, time, inspect, sys
import django.core.exceptions as dexceptions

class Post(models.Model):    
    post_id = models.IntegerField(unique=True)
    date = models.FloatField('Publication date')
    regular_title = models.CharField('Title', max_length=255)
    slug = models.CharField(max_length=255)
    regular_body = models.TextField()
    tumblr_url = models.URLField('Permalink')
    type = models.CharField('Type', max_length=255)
    format = models.CharField(max_length=255)
          
        
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
    
    
#class Settings(models.Model):
#    tumblr_account = models.CharField('Tumblr user address', max_length=255)
#    last_retrieval_date = models.DateTimeField('Last retrieval')
#    cache_time_to_live  = models.IntegerField('Cache time to live')
#    account_name = models.CharField('Account name (optional)', max_length=255)
#    



# not a model but linking the tumblr wrapper with the local cache models

class tumblrPosts(object):
    '''
        methods to retrieve posts from cache and from tumblr,
        sync cache, set settings, etc
        todo: refactor to include only the intermediation between
        model and tumblr. Settings should go in settings model in future
    '''
    
    overrideTTL = None
    
    @classmethod
    def getTumblrPosts(self): 
    # if optionsQuery: options = __queryToOptions(optionsQuery)
        # but first without options
        t_api = Api(self.getTumblrUser())
        return t_api.read()        
    
    @classmethod
    def getTTL(self):
        return self.overrideTTL or  settings.TUMBLRBLOG_CACHE_TIME_TO_LIVE
    
    @classmethod
    def getTumblrUser(self):
        return settings.TUMBLRBLOG_TUMBLR_USER
    
    @classmethod
    def setOverrideTTL(self,ttl):
        '''
        set the time to live for the cache of the posts,
        in minutes, overriding the global setting
        '''
        self.overrideTTL = ttl
        
    # todo: setter and getter settings
    
    # todo: check the time of last checking, when that is implemented
    @classmethod
    def refreshCacheNeeded(self, latest_in_cache_time=None):
        if latest_in_cache_time == None:
            try:
                latest_in_cache_time = Post.objects.all().order_by('date')[:1]['date']
            except:
                return True
        cache_time = datetime.timedelta(minutes=self.getTTL())
    
        if cache_time == 0: return self.checkCacheSync() # we want to refresh everytime
        # if the TTL has passed, refresh
        # we use last entry on cache while db settings with last_refresh is not implemented
    
        if datetime.datetime.fromtimestamp(latest_in_cache_time) <= (datetime.datetime.now() - cache_time): 
            return self.checkCacheSync()
        
        return False   
    
    @classmethod
    def checkCacheSync(self, localItems=None, remoteItems=None):
        '''
            check if there are tumblr posts that are not in cache
            Args: optionally, the two lists of posts to be compared,
                    they are otherwise taken from tumblr api and local cache
            Returns: True if there are posts in Tumblr that are not in cache, False otherwise
        '''
        if localItems==None:
            localItems = self.localPosts()   
        if remoteItems==None:
            remoteItems = self.remotePosts()
            
        return self._comparePostsLists(localItems, remoteItems, ['regular_body','regular-body'])   
            
    @classmethod
    def _comparePostsLists(self,list1, list2, fields):   
        if len(list1) != len(list2): return True
        i = 0
        for post in list1:     
            try:                 
                for field in fields:
                    try: list1hash = hashlib.sha1(post[field])     
                    except KeyError: continue          
            except (TypeError, KeyError):
                list1hash = hashlib.sha1( getattr(post, field) )
            try:
                for field in fields:
                    try: list2hash = hashlib.sha1(list2[i][field]) 
                    except KeyError: continue
            except (TypeError, KeyError):
                list2hash = hashlib.sha1( getattr(list2[i], field) )
            
    #        for post in list1: print vars(post)
    #        for post in list2: print vars(post)
            
            if list1hash.hexdigest() != list2hash.hexdigest():
                return True
            i = i + 1
        return False
        
    @classmethod    
    def syncWithTumblr(self):
            try:
                if self.refreshCacheNeeded():
                    for post in self.getTumblrPosts():
                        #todo: check not already in cache - or will this failed if an existing id is passed?
                        Post.TumblrPostToCache(post)
                return Post.objects.all()
            except Exception: return Post.objects.all()
    
    @classmethod     
    def localPosts(self):
        posts = []
        [ posts.append(post) for post in Post.objects.all().order_by('-date') ]
        return posts
    
    @classmethod
    def remotePosts(self):       
        posts = []
        try:
            [ posts.append(post) for post in Api(self.getTumblrUser()).read() ]
        except TumblrError:
            return posts
        return posts
    
    @classmethod
    def getLatestPosts(self, limit=settings.TUMBLRBLOG_MAX_POSTS_HOME_PAGE):
        self.syncWithTumblr()
        return Post.objects.all().order_by('-date')[:limit]
    
    @classmethod
    def getPost(self, id):
        self.syncWithTumblr()
        try: return Post.objects.get(post_id=id)
        except dexceptions.ObjectDoesNotExist: return False
    
    @classmethod    
    def getPosts(self, date=datetime.datetime.now(), daysback=10, limit=settings.TUMBLRBLOG_MAX_POSTS_HOME_PAGE):
        self.syncWithTumblr()
        dateback = date - datetime.timedelta(days=daysback)
        dateback = time.mktime(dateback.timetuple())
        try: 
            return Post.objects.filter(date__gte=dateback)[:limit]
        except dexceptions.ObjectDoesNotExist: return False
    
    @classmethod        
    def cleanCache(self):
        Post.objects.all().delete()    
        