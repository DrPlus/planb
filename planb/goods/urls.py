from django.conf.urls import patterns, url
from goods import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<categoryId>\d+)/$', views.category, name='category'),
    url(r'^(?P<categoryId>\d+)/offer/(?P<offerId>\d+)/$', views.offer, name='offer'),
)
