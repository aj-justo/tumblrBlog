'''
Created on Jul 10, 2011

@author: ajweb.eu
'''
from tumblr import Api

def get(optionsQuery=''):
    if optionsQuery: options = __queryToOptions(optionsQuery)
    # but first without options
    t_api = Api('ajweb.tumblr.com')
    return t_api.read()
    
        
        

def __queryToOptions(query):
    dict([o.split('=') for o in query.split('&')])