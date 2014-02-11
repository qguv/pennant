from django.conf.urls import patterns, url

from pennant import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^getlist', views.getlist, name='getlist'),
)
