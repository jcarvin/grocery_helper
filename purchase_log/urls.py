__author__ = 'jdcar'

from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),
]