# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from forum.models import Forum, Post, UserGroup
from scraper.items import ForumItem, ThreadItem, PostItem, RawPostItem, UserItem, UserGroupItem

class ZetaboardsPipeline(object):
    """
    Post-processing of zetaboard related items.
    """

    def process_item(self, item, spider):
        """
        Process the various items.
        """
        django_item = None
        # You can't attach pipelines to specific items
        # so unfortunately this is going to result in
        # a big elif branch. 
        if isinstance(item, ForumItem):
            spider.log("Processing Forum Item.")
            if item.get('parent'):
                parent = Forum.objects.get(zeta_id=item['parent'])
            else:
                parent = None
            django_item, created = item.django_model._default_manager.get_or_create(
                                        zeta_id=item['zeta_id'],
                                        defaults={
                                            'title': item['title'],
                                            'parent': parent,
                                            }
                                        )
        elif isinstance(item, ThreadItem):
            spider.log("Processing Thread Item.")
            django_item, created = item.django_model._default_manager.get_or_create(
                                        zeta_id=item['zeta_id'],
                                        defaults={
                                            'username': item['user'],
                                            'forum_id': item['forum'],
                                            'title': item['title'],
                                            'subtitle': item.get('subtitle'),
                                            'replies': item['replies'],
                                            'views': item['views'],
                                            'date_posted': item['date_posted']
                                            }
                                        )
        elif isinstance(item, PostItem):
            spider.log("Processing Post Item.")
            post, created = item.django_model._default_manager.get_or_create(
                                zeta_id=item['zeta_id'],
                                defaults={
                                        'thread_id': item['thread'],
                                        'username': item['username'],
                                        #raw_post_bbcode gets added from RawPostItem
                                        'raw_post_html': item['raw_post_html'],
                                        'ip_address': item['ip_address'],
                                        'date_posted': item['date_posted']
                                    }
                                )
        elif isinstance(item, RawPostItem):
            spider.log("Processing RawPost Item.")
            post = Post.objects.get(zeta_id=item['zeta_id'])
            post.raw_post_bbcode = item['raw_post_bbcode'] 
            post.save()
        elif isinstance(item, UserItem):
            spider.log("Processing User Item.")
            user_group, created = UserGroup.objects.get_or_create(title=item['user_group'])
            django_item, created = item.django_model._default_manager.get_or_create(
                                        zeta_id=item['zeta_id'],
                                        defaults={
                                            'username': item['username'],
                                            'user_group': user_group,
                                            'member_number': item['member_number'],
                                            'post_count': item['post_count'],
                                            'signature': item['signature'],
                                            'date_birthday': item.get('date_birthday'),
                                            'date_joined': item['date_joined'],
                                            }
                                        )
        return django_item
