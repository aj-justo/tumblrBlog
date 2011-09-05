'''
Wrapper to the tumblr API library

Created on Jul 10, 2011
@author: ajweb.eu
'''
from tumblr import Api, TumblrError 
from tumblrBlog import settings, models
import datetime, hashlib, time, inspect
import django.core.exceptions as dexceptions

overrideTTL = None

def getTumblrPosts(): 
# if optionsQuery: options = __queryToOptions(optionsQuery)
    # but first without options
    t_api = Api(getTumblrUser())
    return t_api.read()        

def getTTL():
    global overrideTTL
    return overrideTTL or  settings.TUMBLRBLOG_CACHE_TIME_TO_LIVE

def getTumblrUser():
    return settings.TUMBLRBLOG_TUMBLR_USER

def setOverrideTTL(ttl):
    '''
    set the time to live for the cache of the posts,
    in minutes, overriding the global setting
    '''
    global overrideTTL
    overrideTTL = ttl
    
# todo: setter and getter settings

# todo: check the time of last checking, when that is implemented
def refreshCacheNeeded(latest_in_cache_time=None):
    if latest_in_cache_time == None:
        try:
            latest_in_cache_time = models.Post.objects.all().order_by('date')[:1]['date']
        except:
            return True
    cache_time = datetime.timedelta(minutes=getTTL())

    if cache_time == 0: return checkCacheSync() # we want to refresh everytime
    # if the TTL has passed, refresh
    # we use last entry on cache while db settings with last_refresh is not implemented

    if datetime.datetime.fromtimestamp(latest_in_cache_time) <= (datetime.datetime.now() - cache_time): 
        return checkCacheSync()
    
    return False   

def checkCacheSync(localItems=None, remoteItems=None):
    '''
        check if there are tumblr posts that are not in cache
        Args: optionally, the two lists of posts to be compared,
                they are otherwise taken from tumblr api and local cache
        Returns: True if there are posts in Tumblr that are not in cache, False otherwise
    '''
    if localItems==None:
        localItems = localPosts()   
    if remoteItems==None:
        remoteItems = remotePosts()
        
    return _comparePostsLists(localItems, remoteItems, ['regular_body','regular-body'])   
        

def _comparePostsLists(list1, list2, fields):   
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
    
    
def syncWithTumblr():
        try:
            if refreshCacheNeeded():
                for post in getTumblrPosts():
                    #todo: check not already in cache - or will this failed if an existing id is passed?
                    models.Post.TumblrPostToCache(post)
            return models.Post.objects.all()
        except Exception: return models.Post.objects.all()

     
def localPosts():
    posts = []
    [ posts.append(post) for post in models.Post.objects.all().order_by('-date') ]
    return posts


def remotePosts():
    posts = []
    try:
        [ posts.append(post) for post in Api(getTumblrUser()).read() ]
    except TumblrError:
        return posts
    return posts


def getLatestPosts(limit=settings.TUMBLRBLOG_MAX_POSTS_HOME_PAGE):
    syncWithTumblr()
    return models.Post.objects.all().order_by('-date')[:limit]

def getPost(id):
    syncWithTumblr()
    try: return models.Post.objects.get(post_id=id)
    except dexceptions.ObjectDoesNotExist: return False
    
def getPosts(date=datetime.datetime.now(), daysback=10, limit=settings.TUMBLRBLOG_MAX_POSTS_HOME_PAGE):
    syncWithTumblr()
    dateback = date - datetime.timedelta(days=daysback)
    dateback = time.mktime(dateback.timetuple())
    try: 
        return models.Post.objects.filter(date__gte=dateback[:limit])
    except dexceptions.ObjectDoesNotExist: return False
        
def cleanCache():
    models.Post.objects.all().delete()    