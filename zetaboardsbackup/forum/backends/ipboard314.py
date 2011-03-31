"""
Handles the SQL export to ipboard v3.1.4
"""
from django.template.loader import render_to_string

from zetaboardsbackup.forum.backends.base import BaseExporter
from zetaboardsbackup.forum.models import Forum, Thread, Post, User, UserGroup

class IPBoard314Exporter(BaseExporter):

    def export_users(self):
        context = {'users': User.objects.all()}
        string = render_to_string('backends/ipboard314/export_users.sql', context)
        print string
    
    def export_forums(self):
        pass

    def export_threads(self):
        pass

    def export_posts(self):
        pass


EXPORTER = IPBoard314Exporter
