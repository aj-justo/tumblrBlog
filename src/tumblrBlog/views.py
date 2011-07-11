'''
Created on Jul 8, 2011

@author: ajweb.eu
'''
from django.template import Context, loader
from tumblrBlog.models import Post
from tumblrBlog import tumblrPosts
from django.http import HttpResponse


def index(request):
    posts = Post.latest()
   # posts = tumblrPosts.get()
    template = loader.get_template('tumblrBlog/index.html')
    context = Context({'latest_posts':posts,})
    
    return HttpResponse(template.render(context))

def single(request, post_id):
    post = Post.objects.get(post_id=post_id)
    template = loader.get_template('tumblrBlog/single.html')
    context = Context({'post':post,})
    return HttpResponse(template.render(context))        