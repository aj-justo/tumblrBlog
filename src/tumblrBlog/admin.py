from django.contrib import admin
from django.db import models
from tumblrBlog import models as tumblrBlogModels

class tumblrAdmin(admin.ModelAdmin):
    pass

class adminGeneral(tumblrAdmin):
    tumblrUser = models.CharField(max_length=255, verbose_name="Tumblr user")
    cacheTTL = models.IntegerField(max_length=3,
        verbose_name="Hours before refreshing the cache")

class adminReading(tumblrAdmin):
    postsPerPage = models.IntegerField(max_length=3,
        verbose_name="Number of posts per page")
    excerptLength = models.IntegerField(max_length=3,
        verbose_name="Characters to show for the excerpt (zero if you don't want it)")
    showDate = models.BooleanField("Show date of post in listings")

# These classes will enable showing the current cached posts so the admin
# can set the posts she wants to show or hide
class adminPost(admin.ModelAdmin):
    list_display = ('date', 'regular_title', 'visible')
    actions = ['setVisible', 'setHidden']

    def __init__(self, *args, **kwargs):
        super(adminPost, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def setVisible(self, request, queryset):
        rows_updated = queryset.update(visible=True)
        self.message_user(request, "%s posts have been updated as Visible" % rows_updated)

    def setHidden(self, request, queryset):
        rows_updated = queryset.update(visible=False)
        self.message_user(request, "%s posts have been updated as Hidden" % rows_updated)

    setVisible.short_description = 'Display selected posts'
    setHidden.short_description = 'Hide selected posts'

    def has_add_permission(self, request):
        return False

class adminTag(admin.ModelAdmin):
    list_display = ['tag']

    def __init__(self, *args, **kwargs):
        super(adminTag, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def has_add_permission(self, request):
        return False

admin.site.register(tumblrBlogModels.Post, adminPost)
admin.site.register(tumblrBlogModels.Tag, adminTag)
admin.site.disable_action('delete_selected')

