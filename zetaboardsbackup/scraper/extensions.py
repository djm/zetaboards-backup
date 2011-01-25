from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from forum.models import Thread, Post, User

class SpiderCloseFunctionality(object):

    def __init__(self):
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_closed(self, spider):
        """
        On spider close, put in place the FKs
        from Thread and Post to the User model.
        We can't do this on save as we can't guarantee
        that we've scraped the user object yet.
        """
        for thread in Thread.objects.all():
            try:
                thread.user = User.objects.get(username=thread.username)
                thread.save()
            except User.DoesNotExist:
                pass
        for post in Post.objects.all():
            try:
                post.user = User.objects.get(username=post.username)
                post.save()
            except User.DoesNotExist:
                pass
