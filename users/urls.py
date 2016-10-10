"""Defines url patterns for users."""

from django.conf.urls import url
from django.contrib.auth.views import login

from . import views

urlpatterns = [
    # Login page.
    url(r'^login/$', login, {'template_name': 'users/login.html'},
        name='login'),
        
    # Logout page.
    url(r'^logout/$', views.logout_view, name='logout'),
    
    # Registration page. 
    url(r'^register/$', views.register, name='register'),

    # Friends List.
    url(r'^friends/(?P<user_id>\d+)/$', views.friends, name='friends'),
]
