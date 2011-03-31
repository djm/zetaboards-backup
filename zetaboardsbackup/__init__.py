import logging
import sys
from django.conf import settings

__author__ = 'Darian Moody'
__version__ = (0, 0, 1, 'alpha')
__all__ = ['log']

# Get logging level and formatting settings.
LOGGING_LEVEL = getattr(settings, 'ZETABOARDS_LOGGING_LEVEL', logging.INFO)
LOGGING_FORMAT = getattr(settings, 'ZETABOARDS_LOGGING_FORMAT', 
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Set up the logger, stream handler and proper formatting.
log = logging.getLogger('zetaboards')
formatter = logging.Formatter(LOGGING_FORMAT)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.INFO)
stream.setFormatter(formatter)
log.addHandler(stream)
log.setLevel(LOGGING_LEVEL)
