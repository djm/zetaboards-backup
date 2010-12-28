from django.conf.urls.defaults import *

urlpatterns = patterns('library.views',

    url(r'^$', 'price_grid', name="price_grid"),
    url(r'^graph/(?P<book>[\d]+)/$', 'price_graph', name="price_graph"),
    url(r'^graph/(?P<book>[\d]+)/(?P<shop>[\d+])/$', 'price_graph',
        name="price_graph_shop"),
)
