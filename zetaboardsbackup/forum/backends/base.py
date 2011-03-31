"""
All exporter classes should subclass from this base exporter.
"""

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
        self.export_users()
        self.export_forums()
        self.export_threads()
        self.export_posts()

    def export_users(self):
        raise NotImplementedError

    def export_forums(self):
        raise NotImplementedError

    def export_threads(self):
        raise NotImplementedError

    def export_posts(self):
        raise NotImplementedError
