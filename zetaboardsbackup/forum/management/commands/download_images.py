# encoding: utf-8
"""
Executes the command to find all image URLs in posts and
save the content to local disk.
"""
from django.core.management.base import BaseCommand

from zetaboardsbackup import log
from zetaboardsbackup.forum.models import Post
from zetaboardsbackup.forum.utils import ImageUrlDownloader


class Command(BaseCommand):
    """
    Finds all image urls available in posts and
    makes an attempt at saving them to disk.
    """

    help = 'Downloads all images found in posts.'

    def handle(self, *args, **options):
        """
        Wraps the store_images method.
        """
        log.info("Script initialised.")
        queryset = Post.objects.all()
        fields = ('raw_post_bbcode',)
        downloader = ImageUrlDownloader()
        downloader.download(queryset, fields)
        log.info("Complete.")
