'''
Wrapper to the tumblr API library

Created on Jul 10, 2011
@author: ajweb.eu
'''
from tumblr import Api 
from tumblrBlog import settings
import datetime

def get(): 
# if optionsQuery: options = __queryToOptions(optionsQuery)
    # but first without options
    t_api = Api(settings.TUMBLR_USER)
    return t_api.read()        

def check(latest_in_cache_time):
    cache_time = datetime.timedelta(hours=settings.CACHE_HOURS_TO_LIVE)
    if latest_in_cache_time < datetime.datetime.now() - cache_time: 
        return False
    latest_in_tumblr = Api(settings.TUMBLR_USER).read(settings.TUMBLR_USER, 0, 1)['unix-timestamp']
    if latest_in_tumblr == latest_in_cache_time:
        return False
    return True   
       

def __queryToOptions(query):
    dict([o.split('=') for o in query.split('&')])
    
