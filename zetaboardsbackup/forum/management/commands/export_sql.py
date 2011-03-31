# encoding: utf-8
"""
Executes the command to export SQL in a relevant format for another forum.
"""
from optparse import make_option

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from zetaboardsbackup import log


class Command(BaseCommand):
    """
    Finds all image urls available in posts and
    makes an attempt at saving them to disk.
    """

    help = 'Downloads all images found in posts.'

    option_list = BaseCommand.option_list + (
        make_option(
            '-f',
            '--forum',
            action='store',
            type="string",
            nargs=1,
            dest='forum',
            help='If used, will force a hard refresh and re-download of all images.'
        ),
    )

    def handle(self, *args, **options):
        """
        Wraps the store_images method.
        """
        log.info("Export script initialised.")
        forum = options.get('forum')
        if forum:
            try:
                module = __import__('zetaboardsbackup.forum.backends.%s' % forum, fromlist=['EXPORTER'])
                klass = getattr(module, 'EXPORTER')
            except (ImportError, AttributeError), e:
                raise ImproperlyConfigured("%s: check your --forum flag, are you sure that backend exists?" % e)
            else:
                backend = klass()
                backend.export()
        else:
            log.error("The --forum flag (-f) was not provided. Please provide the backend you wish to export to.")
        log.info("Complete.")
