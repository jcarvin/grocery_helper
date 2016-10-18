from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import User
from friendship.models import Friend, FriendshipRequest
from django.contrib.auth.decorators import login_required

from .forms import UserCreateForm, AddFriendForm


def logout_view(request):
    """Log the user out."""
    logout(request)
    return HttpResponseRedirect(reverse('purchase_log:index'))


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form.   
        form = UserCreateForm()
    else:
        # Process completed form.
        form = UserCreateForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            # Log the user in, and then redirect to home page.
            authenticated_user = authenticate(username=new_user.username,
                password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('index:index'))

    context = {'form': form}
    return render(request, 'users/register.html', context)


def friends(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    friend_list = [friend for friend in Friend.objects.friends(request.user)]
    context = {
        'user': user,
        'friend_list': friend_list,
    }
    return render(request, 'users/friends.html', context)


@login_required
def add_friend(request):
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddFriendForm
        status_message = ''
    else:
        # POST data submitted; process data.
        form = AddFriendForm(data=request.POST)
        status_message = ''
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if email not in [user.email for user in User.objects.all()]:
                status_message = 'No user with that email.'
            else:
                r_list = [f_request for f_request in Friend.objects.unrejected_requests(user=User.objects.get(email=email))
                          if f_request.from_user == request.user]

                if email == request.user.email:
                    status_message = 'You cannot add yourself as a friend.'
                elif len(r_list) >= 1:
                    status_message = 'You have already sent a request to that user.'
                elif Friend.objects.are_friends(request.user, User.objects.get(email=email)):
                    status_message = 'You are already friends with ' + User.objects.get(email=email).username + '.'
                else:
                    status_message = 'Friend request sent!'

        if form.is_valid() and status_message == 'Friend request sent!':
            email = form.cleaned_data.get('email')
            other_user = User.objects.get(email=email)
            Friend.objects.add_friend(
                request.user,                               # The sender
                other_user,                                 # The recipient
                message='Hi! I would like to add you')
    context = {'form': form, 'status_message': status_message}
    return render(request, 'users/add_friend_form.html', context)


def inbox(request, user_id):
    unread_friend_request_list = [request for request in
                                  Friend.objects.unread_requests(user=request.user)]
    read_friend_request_list = [request for request in
                                Friend.objects.unrejected_requests(user=request.user)
                                if request not in unread_friend_request_list]
    context = {
        'unread_friend_request_list': unread_friend_request_list,
        'read_friend_request_list': read_friend_request_list,
    }
    return render(request, 'users/inbox.html', context)


def request_details(request, f_request_id):
    f_request = FriendshipRequest.objects.get(pk=f_request_id)
    f_request.mark_viewed()
    context = {
        'f_request': f_request,
    }
    return render(request, 'users/f_request_details.html', context)


def accept_request(request, f_request_id):
    f_request = FriendshipRequest.objects.get(pk=f_request_id)
    f_request.accept()
    return HttpResponseRedirect(reverse('users:inbox', args=[request.user.id]))


def decline_request(request, f_request_id):
    f_request = FriendshipRequest.objects.get(pk=f_request_id)
    f_request.reject()
    return HttpResponseRedirect(reverse('users:inbox', args=[request.user.id]))


def ignore_request(request, f_request_to_user_id):
    return HttpResponseRedirect(reverse('users:inbox', args=[request.user.id]))


def delete_friend(request, friend_id):
    Friend.objects.remove_friend(request.user, User.objects.get(id=friend_id))
    return HttpResponseRedirect(reverse('users:friends', args=[request.user.id]))