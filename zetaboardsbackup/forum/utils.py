import httplib
import re
import socket
import urllib2

from django.conf import settings

from zetaboardsbackup import log

# Timeout for requests in seconds.
timeout = 4
socket.setdefaulttimeout(timeout)

IMAGE_SAVE_PATH = getattr(settings, 'ZETABOARDS_IMAGE_SAVE_PATH', 
                            "%s/downloaded-images/" % settings.MEDIA_ROOT)

class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    """
    Simple urllib error handler, attaches status code to
    response and returns.
    """

    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result   

class ImageUrlDownloader(object):
    """
    Handles all related this related
    to downloading image urls.
    """
    
    def download(self, queryset, fields, save_path=IMAGE_SAVE_PATH):
        """
        Takes in a Django queryset and an iterative
        of field names as strings to search for image
        URLs to download.
        """
        data_to_search = []
        urls_to_download = []
        # For every item in the fieldset, check the fields for
        # data to add to our of things to search for urls.
        for item in queryset:
            for field in fields:
                text = getattr(item, field)
                if text:
                    data_to_search.append(text)
        # Extract all possible image urls from the data.
        for text in data_to_search:
            urls = self._extract_image_urls(text)
            if urls:
                log.debug("Found URLs: %s" % urls)
                urls_to_download += urls
        # Attempt to download and save all the URLs found.
        for url in urls_to_download[::-1]:
            self._do_download(url, save_path)


    def _extract_image_urls(self, text):
        """
        Given a chunk of text, returns a list of 
        all matched URIs that point to images.
        """
        image_urls = []
        # Break up adjacent bbtags.
        text = text.replace('][', '] [')
        url_re = re.compile("(https?\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(?:\/\S*)?(?:[a-zA-Z0-9_])+\.(?:jpg|jpeg|gif|png|bmp|svg))", re.IGNORECASE)
        matches = url_re.findall(text)
        if matches:
            image_urls += matches
        return image_urls

    def _do_download(self, url, save_path):
        """
        Attempts to retrieve the image from the remote URL.
        """
        opener = urllib2.build_opener(DefaultErrorHandler())
        request = urllib2.Request(url)
        filename = url.rsplit('/', 1)[-1]
        filename = "%s%s" % (save_path, filename)
        try:
            image_file = open(filename, "r")
        except IOError:
            try:
                datastream = opener.open(request)
            except urllib2.URLError, e:
                log.error("[ERROR] %s <%s>" % (e, url))
                datastream = None
                pass
            except httplib.BadStatusLine, e:
                log.error("[ERROR] %s <%s>" % (e, url))
                datastream = None
                pass
            if datastream:
                if hasattr(datastream, 'status'):
                    log.error("[ERROR: HTTP %s] %s" % (datastream.status, url))
                else:
                    image_file = open(filename, "wb")
                    image_file.write(datastream.read())
                    image_file.close()
                    log.info("[SUCCESS] Image downloaded and saved. <%s>" % url)
        else:
            image_file.close()
            log.info("[EXISTS] File exists already. <%s>" % url)
