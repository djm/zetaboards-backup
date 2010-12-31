# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from forum.models import Forum
from scraper.items import ForumItem, ThreadItem, PostItem, UserItem, UserGroupItem

class ZetaboardsPipeline(object):
    """
    Post-processing of zetaboard related items.
    """

    def process_item(self, item, spider):
        """
        Process the various items.
        """
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
                                            },
                                        )
        elif isinstance(item, ThreadItem):
            spider.log("Processing Thread Item.")
        elif isinstance(item, PostItem):
            spider.log("Processing Post Item.")
        elif isinstance(item, UserItem):
            spider.log("Processing User Item.")
        elif isinstance(item, UserGroupItem):
            spider.log("Processing UserGroup Item.")
        return django_item
