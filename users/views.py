from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import User
from friendship.models import Friend
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

    def get_status_message(from_user, to_user):
        for f_request in Friend.objects.unrejected_requests(user=from_user):
            if f_request.to_user == to_user:
                return 'You have already sent that user a request.'
            # elif from_user.email == to_user.email:
            #     return 'You cannot add yourself as a friend.'
            # elif Friend.objects.are_friends(from_user, to_user):
            #     return 'You are already friends with ' + to_user.username + '.'
            # elif User.objects.filter(email=to_user.email).count() == 0:
            #     return 'No user with that email.'
            else:
                return 'Friend request sent!'

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddFriendForm
        status_message = 'test'
    else:
        # POST data submitted; process data.
        form = AddFriendForm(data=request.POST)
        status_message = 'test'
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


# def inbox(request, user_id):