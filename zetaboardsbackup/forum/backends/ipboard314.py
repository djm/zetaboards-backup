"""
Handles the SQL export to ipboard v3.1.4
"""
from django.template.loader import render_to_string

from zetaboardsbackup.forum.backends.base import BaseExporter
from zetaboardsbackup.forum.models import Forum, Thread, Post, User

class IPBoard314Exporter(BaseExporter):

    def export_users(self):
        context = {'users': User.objects.all()}
        rendered = render_to_string('backends/ipboard314/export_users.sql', context)
        return rendered
    
    def export_forums(self):
        context = {'forums': Forum.objects.all()}
        rendered = render_to_string('backends/ipboard314/export_forums.sql', context)
        return rendered

    def export_threads(self):
        context = {'threads': Thread.objects.all()}
        rendered = render_to_string('backends/ipboard314/export_threads.sql', context)
        return rendered

    def export_posts(self):
        context = {'posts': Post.objects.all()}
        rendered = render_to_string('backends/ipboard314/export_posts.sql', context)
        return rendered


EXPORTER = IPBoard314Exporter
