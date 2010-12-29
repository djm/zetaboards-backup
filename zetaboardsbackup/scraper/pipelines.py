# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

class ZetaboardsPipeline(object):
    """
    Post-processing of zetaboard related items.
    """

    def process_item(self, item, spider):
        return None
