"""
Created on Jul 7, 2011

@author: aj
"""
from django.db import models
from util.tumblr import Api, TumblrError 
from tumblrBlog import settings
import datetime, time
import django.core.exceptions as dexceptions

class Post(models.Model):    
    post_id = models.IntegerField(unique=True)
    date = models.DateTimeField('Publication date')
    regular_title = models.CharField('Title', max_length=255)
    slug = models.CharField(max_length=255)
    regular_body = models.TextField()
    tumblr_url = models.URLField('Permalink')
    type = models.CharField('Type', max_length=255)
    format = models.CharField(max_length=255)
    visible = models.BooleanField()

    class Meta:
        app_label = 'tumblrBlog'
          
        
    @classmethod
    def TumblrPostToCache(cls, post):
        cpost = Post()
        cpost.post_id = post['id']
        cpost.date = datetime.datetime.fromtimestamp( post['unix-timestamp'] )
        cpost.regular_title = post['regular-title']
        cpost.regular_body = post['regular-body']
        cpost.type = post['type']
        cpost.format = post['format']
        cpost.tumblr_url = post['url']
        cpost.slug = post['slug']
        cpost.visible = True
        cpost.save()
        
       

class Tag(models.Model):
    tag_id = models.IntegerField()
    post_id = models.ForeignKey(Post)
    tag = models.CharField(max_length=255)

    class Meta:
        app_label = 'tumblrBlog'



    
#class Settings(models.Model):
#    tumblr_account = models.CharField('Tumblr user address', max_length=255)
#    last_retrieval_date = models.DateTimeField('Last retrieval')
#    cache_time_to_live  = models.IntegerField('Cache time to live')
#    account_name = models.CharField('Account name (optional)', max_length=255)
#    



# not a model but linking the tumblr wrapper with the local cache models

class tumblrPosts(object):
    """
        methods to retrieve posts from cache and from tumblr,
        sync cache, set settings, etc
        todo: refactor to include only the mediation between
        model and tumblr. Settings should go in settings model in future
    """
    
    overrideTTL = None
    
    @classmethod
    def getTumblrPosts(cls):
        # if optionsQuery: options = __queryToOptions(optionsQuery)
        # but first without options
        t_api = Api(cls.getTumblrUser())
        return t_api.read()        
    
    @classmethod
    def getTTL(cls):
        return cls.overrideTTL or  settings.TUMBLRBLOG_CACHE_TIME_TO_LIVE
    
    @classmethod
    def getTumblrUser(cls):
        return settings.TUMBLRBLOG_TUMBLR_USER
    
    @classmethod
    def setOverrideTTL(cls,ttl):
        """
        set the time to live for the cache of the posts,
        in minutes, overriding the global setting
        """
        cls.overrideTTL = ttl
        
    # todo: setter and getter settings
    # todo: check the time of last checking, when that is implemented
    @classmethod
    def refreshCacheNeeded(cls, latest_in_cache_time=None):
        if latest_in_cache_time is None:
            try:
                latest_in_cache_time = Post.objects.all().order_by('date')[:1]['date']
            except Exception:
                return True
        cache_time = datetime.timedelta(hours=cls.getTTL())
        if not cache_time: return cls.checkCacheSync() # we want to refresh everytime
        # if the TTL has passed, refresh
        # we use last entry on cache while db settings with last_refresh is not implemented
        if datetime.datetime.fromtimestamp(latest_in_cache_time) \
                <= (datetime.datetime.now() - cache_time):
            return cls.checkCacheSync()
        return False

    @classmethod
    def checkCacheSync(cls, localItems=None, remoteItems=None):
        """
            check if there are tumblr posts that are not in cache
            Args: optionally, the two lists of posts to be compared,
                    they are otherwise taken from tumblr api and local cache
            Returns: True if there are posts in Tumblr that are not in cache, False otherwise
        """
        if localItems is None:
            localItems = cls.localPosts()
        if remoteItems is None:
            remoteItems = cls.remotePosts()
        return cls.__arePostsListsEqual(localItems, remoteItems, ['regular_body','regular-body'])

    @classmethod
    def __arePostsListsEqual(cls, list1, list2, fields):
        if len(list1) != len(list2): return True
        if cls.__getListOfPostsFields(list1, fields) != \
            cls.__getListOfPostsFields(list2, fields): return True
        return False

    @classmethod
    def __getListOfPostsFields(cls, postsList, fields):
        filteredList = []
        for post in postsList:
            for field in fields:
                try:
                    try: filteredList = post[field]
                    except KeyError: continue
                except (TypeError, KeyError):
                    try: filteredList = getattr(post, field)
                    except AttributeError: continue
        return filteredList
        
    @classmethod    
    def syncWithTumblr(cls):
        try:
            if cls.refreshCacheNeeded():
                for post in cls.getTumblrPosts():
                    #todo: check not already in cache - or will this failed if an existing id is passed?
                    Post.TumblrPostToCache(post)
            return Post.objects.all()
        except Exception: return Post.objects.all()
    
    @classmethod     
    def localPosts(cls):
        posts = []
        [ posts.append(post) for post in Post.objects.all().order_by('-date') ]
        return posts
    
    @classmethod
    def remotePosts(cls):
        posts = []
        try:
            [ posts.append(post) for post in Api(cls.getTumblrUser()).read() ]
        except TumblrError:
            return posts
        return posts
    
    @classmethod
    def getLatestPosts(cls, limit=settings.TUMBLRBLOG_MAX_POSTS_HOME_PAGE):
        cls.syncWithTumblr()
        return Post.objects.all().filter(visible=True).order_by('-date')[:limit]
    
    @classmethod
    def getPost(cls, id):
        cls.syncWithTumblr()
        try: return Post.objects.get(post_id=id, visible=True)
        except dexceptions.ObjectDoesNotExist: return False
    
    @classmethod    
    def getPosts(cls, date=datetime.datetime.now(), daysback=10, limit=settings.TUMBLRBLOG_MAX_POSTS_HOME_PAGE):
        cls.syncWithTumblr()
        dateback = date - datetime.timedelta(days=daysback)
#        dateback = time.mktime(dateback.timetuple())
        try:
            return Post.objects.filter(date__gte=dateback, visible=True)[:limit]
        except dexceptions.ObjectDoesNotExist: return False
    
    @classmethod        
    def cleanCache(cls):
        Post.objects.all().delete()
        