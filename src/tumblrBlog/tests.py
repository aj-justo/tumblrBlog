'''
Created on Jul 11, 2011

@author: aj
'''
import unittest
from tumblrBlog import models, settings
# to use tumblrPosts.xxx as before the refactoring
from tumblrBlog.models import tumblrPosts
import datetime, time, random
import django.core.exceptions as dexceptions


class TestUnits(unittest.TestCase):
    '''
        these tests are for the internals of the app.
        They have been used for the development of the app 
        but you should not need to run them if you are going to
        modify the app 
    '''
        
    ids = []
      
    def setUp(self):
        pass

    def tearDown(self):
        tumblrPosts.cleanCache()

    def generateTestPosts(self, limit):       
        posts = []
        while limit > 0:
            id = random.randint(1000000,10000000)
            post = models.Post(                        
                    post_id=id,
                    date=time.time(),
                    regular_title='This is a test',
                    slug='this-is-a-test',
                    regular_body='testing the test : ' + str(id),
                    tumblr_url='http://ajweb.es',
                    type='regular',
                    format='text'
                    )
            posts.append(post)
            limit -= 1
            self.ids.append(id)
        return posts

    def savePostsToCache(self, posts):
        [post.save() for post in posts]
    
    def testRetrieveFromTumblr(self):
        self.assertTrue(datetime.datetime.fromtimestamp(tumblrPosts.getTumblrPosts().next()['unix-timestamp']))
    
    def testSaveAndDeletePostToDb(self):
        post = models.Post(
                    post_id=1005,
                    date=time.time(),
                    regular_title='This is a test',
                    slug='this-is-a-test',
                    regular_body='testing the test',
                    tumblr_url='http://ajweb.es',
                    type='regular',
                    format='text'
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
        self.savePostsToCache(self.generateTestPosts(5))
        localPosts = tumblrPosts.__localPosts()
        # assuming posts are already synced
        self.assertFalse(tumblrPosts.checkCacheSync(localPosts, localPosts))
        self.savePostsToCache(self.generateTestPosts(2))
        localPosts2 = tumblrPosts.__localPosts()
        self.assertTrue(tumblrPosts.checkCacheSync(localPosts, localPosts2))
        
    # it DOES CONNECT to tumblr    
    def testRealSyncTumblrWithCache(self):
        models.Post.objects.all().delete()
        tumblrPosts.syncWithTumblr()
        self.assertFalse(tumblrPosts.checkCacheSync())


class TestCase(unittest.TestCase):
    '''
        these test the public API of the app
        as it would be used from a django view
    '''
    sampleId = 7225327240
    
    def tearUp(self):       
        pass
    
    def tearDown(self):
        tumblrPosts.cleanCache()
    
    def testGetLatestPosts(self):
        latest = tumblrPosts.getLatestPosts(10)
        for post in latest:
            self.assertTrue(post.post_id) 
            self.assertEquals(type(post.regular_body), type(u''))
            self.assertTrue(datetime.datetime.fromtimestamp(post.date))
            
    def testGetIndividualPost(self):
        post = tumblrPosts.getPost(id=self.sampleId)
        self.assertEquals(type(post.date), type(0.01))
        self.assertEquals(type(post.regular_body), type(unicode('')))
        
    def testGetPostsInDateRange(self):
        posts = tumblrPosts.getPosts(date=datetime.datetime.now(), daysback=300)
        self.assertTrue(len(posts) > 0)
        for post in posts:
            self.assertEquals(type(long(self.sampleId)), type(post.post_id))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTumblrPostsGetPosts']
    unittest.main()
