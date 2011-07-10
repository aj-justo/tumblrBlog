'''
Created on Jul 10, 2011

@author: ajweb.eu
'''
from django import template
register = template.Library()

def getkey(value, arg):
    return value[arg]

register.filter('getkey', getkey)
