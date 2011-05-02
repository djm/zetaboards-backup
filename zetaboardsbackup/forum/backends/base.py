"""
All exporter classes should subclass from this base exporter.
"""

from django.utils.encoding import smart_str

from zetaboardsbackup import log

class BaseExporter(object):
    """
    The base SQL exporter, subclass from this.
    """

    def export(self):
        """
        Runs the export process.
        """
        log.info("Exporter initialised.")
        output = u""
        #output += self.export_users()
        #output += self.export_forums()
        output += self.export_threads()
        output += self.export_posts()
        f = open('output.sql', 'w')
        f.write(smart_str(output))
        f.close()

    def export_users(self):
        raise NotImplementedError

    def export_forums(self):
        raise NotImplementedError

    def export_threads(self):
        raise NotImplementedError

    def export_posts(self):
        raise NotImplementedError
