from django.conf.urls import url
from . import views

urlpatterns = [
    # finances/
    url(r'^$', views.index, name='index'),
]