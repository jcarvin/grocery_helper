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

    # Search friends.
    url(r'^add_friend/$', views.add_friend, name='add_friend'),

    # Inbox: /users/inbox/<user.id>
    url(r'^inbox/(?P<user_id>\d+)/$', views.inbox, name='inbox'),

    # Friend Request Details
    url(r'^request/(?P<f_request_id>\d+)/$', views.request_details, name='request_details'),

    # Accept Request
    url(r'^accept/(?P<f_request_id>\d+)/$', views.accept_request, name='accept_request'),

    # Decline Request
    url(r'^decline/(?P<f_request_id>\d+)/$', views.decline_request, name='decline_request'),

    # Ignore Request
    url(r'^ignore/(?P<f_request_to_user_id>\d+)/$', views.ignore_request, name='ignore_request'),

    # Delete Friend
    url(r'^Delete/(?P<friend_id>\d+)/$', views.delete_friend, name='delete_friend'),
]
