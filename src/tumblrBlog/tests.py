"""
Created on Jul 11, 2011
@author: aj
"""

import unittest
from tumblrBlog import models, settings
# to use tumblrPosts.xxx as before the refactoring
from tumblrBlog.models import tumblrPosts
import datetime, time, random
import django.core.exceptions as dexceptions

def generateTestPosts(limit):
    posts = []
    while limit > 0:
        id = random.randint(1000000,10000000)
        post = models.Post(
            post_id=id,
            date=datetime.datetime.utcnow(),
            regular_title='This is a test',
            slug='this-is-a-test',
            regular_body='testing the test : ' + str(id),
            tumblr_url='http://ajweb.es',
            type='regular',
            format='text',
            visible= True
        )
        posts.append(post)
        limit -= 1
    return posts



class DevTests(unittest.TestCase):
        

    def setUp(self):
        posts = generateTestPosts(limit=10)
        self.savePostsToCache(posts)

    def tearDown(self):
        tumblrPosts.cleanCache()

    def savePostsToCache(self, posts):
        for post in posts: post.save()
    
    def testRetrieveFromTumblr(self):
        self.assertTrue(type(tumblrPosts.remotePosts(tumblrAPI)[0]['unix-timestamp'])==type(1.0))
    
    def testSaveAndDeletePostToDb(self):
        post = models.Post(
                    post_id=1005,
                    date=datetime.datetime.utcnow(),
                    regular_title='This is a test',
                    slug='this-is-a-test',
                    regular_body='testing the test',
                    tumblr_url='http://ajweb.es',
                    type='regular',
                    format='text',
                    visible = True
                    )
        post.save()
        self.assertTrue(models.Post.objects.get(post_id=1005))
        post.delete()
        self.assertRaises(dexceptions.ObjectDoesNotExist, models.Post.objects.get, post_id=1005)
        
    def testCacheSetAndGetSetting(self):
        self.assertEquals(type(1), type(settings.TUMBLRBLOG_CACHE_TIME_TO_LIVE)) 
        tumblrPosts.setOverrideTTL(10)
        self.assertEquals(10, tumblrPosts.getTTL())  
    
    def testSyncIsOnWhenCacheOff(self):
        tumblrPosts.setOverrideTTL(0)
        # time is now, so with any TTL > 0 it should NOT refresh
        # with TTL=0 should always refresh
        self.assertTrue(tumblrPosts.refreshCacheNeeded(time.time())) 
        tumblrPosts.setOverrideTTL(10)
        self.assertFalse(tumblrPosts.refreshCacheNeeded(time.time()))
    
    # it does NOT need to connect to tumblr
    def testLocalAndRemotePostsSynced(self):
        self.savePostsToCache(generateTestPosts(5))
        localPosts = tumblrPosts.localPosts()
        # passing same lists of posts should return True
        self.assertTrue(tumblrPosts.isCacheSynced(localItems=localPosts, remoteItems=localPosts))
        self.savePostsToCache(generateTestPosts(2))
        localPosts2 = tumblrPosts.localPosts()
        # it should require syncing if the lists of posts are not identical
        self.assertFalse(tumblrPosts.isCacheSynced(localItems=localPosts, remoteItems=localPosts2))

    def testSaveTumblrPostToCache(self):
        post = tumblrPosts.remotePosts(tumblrAPI)[0]
        models.Post.TumblrPostToCache(post)

    # it DOES CONNECT to tumblr    
    def testSyncTumblrWithCache(self):
        tumblrPosts.setOverrideTTL(0)
        models.Post.objects.all().delete()
        remotePosts = tumblrPosts.remotePosts(tumblrAPI)
        tumblrPosts.syncLocalPostsWith(remotePosts)
        localPosts = tumblrPosts.localPosts()
        self.assertTrue(tumblrPosts.isCacheSynced(localItems=localPosts, remoteItems=remotePosts))


class APItests(unittest.TestCase):
    """
        these test the public API of the app
        as it would be used from a django view
    """

    def setUp(self):
        posts = generateTestPosts(limit=10)
        for post in posts: post.save()
    
    def tearDown(self):
        tumblrPosts.cleanCache()
    
    def testGetLatestPosts(self):
        latest = tumblrPosts.getLatestPosts(10)
        for post in latest:
            self.assertTrue(post.post_id) 
            self.assertEquals(type(post.regular_body), type(u''))

    def testGetIndividualPost(self):
        id = models.Post.objects.all()[0].post_id
        post = tumblrPosts.getPost(id=id)
        self.assertEquals(type(post.date), type(datetime.datetime.utcnow()))
        self.assertEquals(type(post.regular_body), type(unicode(' ')))
        
    def testGetPostsInDateRange(self):
        posts = tumblrPosts.getPosts(date=datetime.datetime.now(), daysback=300)
        self.assertTrue(len(posts) > 0)
        for post in posts:
            self.assertEquals( type(1), type(post.post_id))


class tumblrAPI:
    """
    mock class of the tumblrAPI wrapper used by tumblrBlog.models
    """
    def __init__(self, tumblrUser):
        pass

    def read(self):
        """
        returns an iterable object with the posts
        """
        return self.generateTestTumblrFromModelPosts(generateTestPosts(10))

    def generateTestTumblrFromModelPosts(self, modelPosts):
        posts = []
        for mpost in modelPosts:
            post = {}
            post['id'] = mpost.post_id
            post['unix-timestamp'] = time.mktime( mpost.date.timetuple() )
            post['regular-title'] = mpost.regular_title
            post['regular-body'] = mpost.regular_body
            post['type'] = mpost.type
            post['format'] = mpost.format
            post['url'] = mpost.tumblr_url
            post['slug'] = mpost.slug
            posts.append(post)
        return posts

if __name__ == "__main__":
    unittest.main()
