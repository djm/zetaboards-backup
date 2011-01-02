import os
import sys

parent_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
