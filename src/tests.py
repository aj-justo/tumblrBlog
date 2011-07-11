'''
Created on Jul 11, 2011

@author: aj
'''
import unittest
from tumblrBlog import tumblrPosts
import datetime

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testTumblrPostsGetPosts(self):
        self.assertTrue( len(tumblrPosts.get().next())>0 )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTumblrPostsGetPosts']
    unittest.main()